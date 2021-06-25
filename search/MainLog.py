from .InitializationError import InitializationError
from datetime import datetime, timedelta
from .Config import BaseConfig
from .DHCP2RAD import DHCP2RAD
from .DHCP import DHCP
import re


class MainLog:
    # region class initialization
    def __init__(self, line, *args, **kwargs):
        """Class for processing and storing data from the web log.

        Args:
            line (str): String line from web log.

        Raises:
            InitializationError: If the string does not match the pattern, an error is thrown.
        """

        if re.search(r"Context:.*?;inIP:.*?;Err:.*?;", line) is None:
            raise InitializationError()
        self.ip_id = None
        self.line = line

        self.context = self._get_context()
        self.error = self._get_error()
        self.time = self._get_time()
        self.ip = self._get_ip()

        self.dhcp2rad_times = list()
        self.answer_times = list()
        self.answer = list()
        self.full = False

    # endregion

    # region get content from line

    def _get_time(self, *args, **kwargs):
        """The function returns the value of the time from the string.

        Returns:
            str: Time from the string.
        """

        year = str(datetime.now().year) + " "
        date_reg = re.search(r"\d+_\d+_", self.line).group(0) + year
        date = re.sub("_", "-", date_reg)
        time_reg = re.search(r".*?\s", self.line).group(0)
        time = datetime.strptime(
            date + re.search(r"\d+:\d+:\d+", time_reg).group(0), "%d-%m-%Y %H:%M:%S"
        )
        return time

    def _get_context(self, *args, **kwargs):
        """The function returns the value of the error column from the string.

        Returns:
            str: Error column from the string.
        """

        context_reg = re.search(r"Context:.*?;", self.line).group(0)
        context = re.sub(r"^Context: |;$", "", context_reg)
        return "null" if context == "" else "'{}'".format(context)

    def _get_ip(self, *args, **kwargs):
        """The function returns the value of the IP address from the string.

        Returns:
            str: IP address from the string.
        """

        inip_reg = re.search(r"inIP:.*?;", self.line).group(0)
        inip = re.sub(r"^inIP: |;$", "", inip_reg)
        return inip

    def _get_error(self, *args, **kwargs):
        """The function returns the value of the error column from the string.

        Returns:
            str: Error column from the string.
        """

        error_reg = re.search(r"Err:.*?;", self.line).group(0)
        error = re.sub(r"^Err: |;$", "", error_reg)
        return "null" if error == "no" else "'{}'".format(error)

    # endregion

    # region string representaion of class
    def __str__(self, *args, **kwargs):
        """The function returns a string representation of an instance of the class.

        Returns:
            str: String representation of an instance of the class.
        """

        payload = "Time: {}, IP: {}, Context: {}, Error: {}\n".format(
            self.time.time(), self.ip, self.context, self.error
        )
        payload += "Other logs:\n"
        for instance in self.answer:
            payload += "\t{}\n".format(instance)
        return payload

    def get_sql_value(self, *args, **kwargs):
        """The function returns the values to be written to the sql database.

        Returns:
            str: values to be written to the sql database.
        """

        return "({}, {}, '{}', {})".format(
            self.ip_id, self.context, str(self.time), self.error
        )

    # endregion

    # region add new instances
    def __add__(self, value, *args, **kwargs):
        """The function accepts a line from the log as input.
            Initializes one of the main classes for storing data.
            If the initialization is successful, then this instance is added to the main aggregator.

        Args:
            value (str): The line from the log
        """

        if isinstance(value, DHCP):
            if str(value.time) in self.answer_times:
                return
            self.full = True
            self.answer_times.append(str(value.time))
            value.difference = self.time - value.time
            self._add_dhcp_instance(value)
        elif isinstance(value, DHCP2RAD):
            if str(value.time) in self.dhcp2rad_times:
                return
            self.full = True
            self.dhcp2rad_times.append(str(value.time))
            self._add_dhcp_instance(value)
        elif isinstance(value, str):
            try:
                dhcp = DHCP(value)
                self._add_dhcp_instance(instance=dhcp, with_time_delta=True)
            except InitializationError:
                pass

    def _add_dhcp_instance(self, instance, with_time_delta=False, *args, **kwargs):
        """The function takes an instance of the DHCP class.
            It can also accept the terms.
            Checks for conditions, if necessary, and adds an instance to storage.

        Args:
            instance (DHCP): DHCP class instance.
            with_time_delta (bool, optional): Condition to check time period. Defaults to False.
        """

        if with_time_delta:
            min_time = instance.time - timedelta(seconds=BaseConfig.DELAY_RANGE)
            max_time = instance.time + timedelta(seconds=BaseConfig.DELAY_RANGE)
            if min_time < self.time < max_time and self.ip == instance.ip:
                self.answer.append(instance)
            return
        self.answer.append(instance)

    # endregion
