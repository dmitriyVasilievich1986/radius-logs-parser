# region import libraries
from .InitializationError import InitializationError
from collections import OrderedDict
from .DHCP2RAD import DHCP2RAD
from datetime import timedelta
from .MainLog import MainLog
from .DHCP import DHCP
from .Config import V3
from .DB import DB

# endregion


class Aggregator:
    # region initializtion
    def __init__(
        self,
        context="full",
        time=600,
        ip_address=None,
        black_list=False,
        *args,
        **kwargs
    ):
        """The main aggregator.
        Accepts and parses a string from the logs.
        Has the functionality of sorting, filtering content.
        Implemented the ability to save data to the database.

        Args:
            context (str, optional): Filtration option.
                'full' - all entries, 'null' - with Context = '' and 'context' - not empty context.
                Defaults to "full".
            time (int, optional): The time span within which to search for records. Defaults to 600.
            ip_address (str, optional): List of ip addresses to select from. Defaults to None.
            black_list (bool, optional): Flag indicating how to select - white / black list. Defaults to False.
        """

        self.ip_address = ip_address or list()
        self.black_list = black_list
        self.logs = OrderedDict()
        self.context = context
        self.logs_count = 1
        self.time = time

    # endregion

    # region work with DataBase

    def save_sqlite(self, path=None, *args, **kwargs):
        """The function saves data to the database."""

        if len(self.logs):
            db = DB(path=path)
            self._insert_ip(db)
            self._insert_main(db)
            db.close()

    def _insert_ip(self, db, *args, **kwargs):
        """The function saves the table 'ip' to the database.

        Args:
            db (DB): DB class instance.
        """

        values = ",".join("('{}')".format(x) for x in list(self.logs.keys()))
        query = "INSERT INTO ip('ip') VALUES {};".format(values)
        db.execute(query)

    def _insert_main(self, db, *args, **kwargs):
        """The function saves the table 'main', 'dhcp', 'dhcp2rad' to the database.

        Args:
            db (DB): DB class instance.
        """

        mains_null, mains_full, dhcp, dhcp2rad = self._get_all_mains_and_dhcp()
        if len(mains_full):
            values = ",".join(x.get_sql_value() for x in mains_full)
            query = "INSERT INTO main('ip_id', 'context', 'time', 'error') VALUES {};".format(
                values
            )
            db.execute(query)
        if len(dhcp):
            values = ",".join(x.get_sql_values() for x in dhcp)
            query = "INSERT INTO dhcp('main_id', 'time', 'mac', 'device', 'text') VALUES {};".format(
                values
            )
            db.execute(query)
        if len(dhcp2rad):
            values = ",".join(x.get_sql_values() for x in dhcp2rad)
            query = "INSERT INTO dhcp2rad('main_id', 'time', 'mac', 'text') VALUES {};".format(
                values
            )
            db.execute(query)
        if len(mains_null):
            values = ",".join(x.get_sql_value() for x in mains_null)
            query = "INSERT INTO main('ip_id', 'context', 'time', 'error') VALUES {};".format(
                values
            )
            db.execute(query)

    # endregion

    # region string representaion of class
    def show(self, only_answered=False, n=5, *args, **kwargs):
        """The function returns a string representation of the data.
            Takes the number of lines to display and the filter condition.

        Args:
            only_answered (bool, optional): A condition for filtering records, with a response. Defaults to False.
            n (Union[int, None], optional): Number of lines to display. Defaults to 5.

        Returns:
            str: String representation of the data.
        """

        if only_answered:
            filtered = self._get_only_with_answer()
            return (
                self.__str__(filtered_list=filtered, n=n)
                if len(filtered)
                else "Matches not found"
            )
        else:
            return self.__str__(n=n)

    def __str__(self, filtered_list=None, n=None, *args, **kwargs):
        """The function takes as input a list of records and a number
            to display information on the screen.
            Returns a string representation of the data.

        Args:
            filtered_list (Union[list, None], optional): List of records. Defaults to None.
            n (Union[int, None], optional): Count of lines, need to show. Defaults to None.

        Returns:
            str: String representation of the data.
        """

        filtered_list = filtered_list or self._get_values()
        n = n and min(n, len(filtered_list)) or len(filtered_list)
        payload = ""
        for main_log in filtered_list[:n]:
            payload += str(main_log)
        payload += "Show: {}, Overall: {}".format(n, len(filtered_list))
        return payload

    # endregion

    # region filtration
    def _get_values(self, *args, **kwargs):
        """The function returns all the values stored in the dictionary logs.

        Returns:
            list: Values stored in the dictionary logs.
        """

        payload = list()
        for x in list(self.logs.values()):
            payload += x
        return payload

    def _get_all_mains_and_dhcp(self, *args, **kwargs):
        """The function returns a list of MainLog, DHCP, DHCP2RAD instances.

        Returns:
            tuple: List of MainLog, DHCP, DHCP2RAD instances.
        """

        mains_full = list()
        mains_null = list()
        dhcp2rad = list()
        dhcp = list()
        mains = self._get_values()
        for main in mains:
            if main.full:
                mains_full.append(main)
            else:
                mains_null.append(main)
            for d in main.answer:
                d.main_id = len(mains_full)
                if isinstance(d, DHCP):
                    dhcp.append(d)
                elif isinstance(d, DHCP2RAD):
                    dhcp2rad.append(d)
        return mains_null, mains_full, dhcp, dhcp2rad

    def _get_only_with_answer(self, *args, **kwargs):
        """The function returns a list of records that have a response.

        Returns:
            list: List of records that have a response.
        """

        filtered = list(filter(lambda x: x.full, self._get_values()))
        return filtered

    def _get_all_dhcp(self, mains, *args, **kwargs):
        """The function returns a list of DHCP instances.

        Args:
            mains (list): lsit of MainLog instances.

        Returns:
            list: List of DHCP instances.
        """

        payload = list()
        for m in mains:
            payload += m.answer
        return payload

    # endregion

    # region add new instances
    def __add__(self, value, *args, **kwargs):
        """The function accepts a line from the log as input.
            Initializes one of the main classes for storing data.
            If the initialization is successful, then this instance is added to the main aggregator.

        Args:
            value (str): The line from the log
        """

        try:
            main_log = MainLog(value)
            self._add_main_log_instance(main_log)
            return
        except InitializationError:
            pass
        try:
            dhcp = DHCP(value)
            self._add_dhcp_instance(dhcp)
            return
        except InitializationError:
            pass
        try:
            dhcp2rad = DHCP2RAD(value)
            self._add_dhcp_instance(dhcp2rad)
            return
        except InitializationError:
            pass

    def _add_main_log_instance(self, instance, *args, **kwargs):
        """The function accepts an instance of the MainLog class as input.
            Checks the given instance for compliance with the conditions.
            If the conditions are met, then it adds the instance to storage,
            otherwise it raises an initialization error.

        Args:
            instance (MainLog): Instance of the MainLog class

        Raises:
            InitializationError: Checking for preconditions.
        """

        # If there is a condition for the presence / absence of content in the "Context" value.
        if self.context == "context" and instance.context == "null":
            raise InitializationError()
        if self.context == "null" and instance.context != "null":
            raise InitializationError()

        # If there is a condition for selection by ip addresses.
        if (instance.ip not in self.ip_address and self.black_list) or (
            instance.ip in self.ip_address and not self.black_list
        ):
            raise InitializationError()

        # We check if there is already a record with this ip address.
        # If so, we add an instance, otherwise we create a new record.
        if self.logs.get(instance.ip, False):
            instance.ip_id = self.logs[instance.ip][0].ip_id
            self.logs[instance.ip].append(instance)
        else:
            instance.ip_id = self.logs_count
            self.logs_count += 1
            self.logs[instance.ip] = [instance]

    def _add_dhcp_instance(self, instance, *args, **kwargs):
        """The function accepts an instance of the DHCP class as input.
            Attempts to find a record that fits the time frame.
            If there is such a record, then it saves this instance to the main aggregator.

        Args:
            instance (DHCP): Instance of the DHCP class.
        """

        # set time period
        # min_time = instance.time - timedelta(seconds=self.time)
        max_time = instance.time + timedelta(seconds=self.time)

        # get all records with this ip addres
        data = self.logs.get(instance.ip, [])

        # We have all records that is included in the time frame
        filtered_data = filter(lambda x: instance.time <= x.time < max_time, data)
        for main_log in filtered_data:
            main_log + instance

    # endregion
