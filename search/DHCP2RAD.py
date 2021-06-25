from .InitializationError import InitializationError
from datetime import datetime
import re


class DHCP2RAD:
    # region class initialization
    def __init__(self, line, *args, **kwargs):
        """Class for processing and storing data from the dhcp2rad log.

        Args:
            line (str): String line from dhcp2rad log.

        Raises:
            InitializationError: If the string does not match the pattern, an error is thrown.
        """

        if re.search(r"Response", line) is None:
            raise InitializationError()
        self.main_id = None
        self.line = line

        self.time = self._get_time()
        self.mac = self._get_mac()
        self.ip = self._get_ip()

    # endregion

    # region get parsed data from line from log
    def _get_time(self, *args, **kwargs):
        """The function returns the value of the time from the string.

        Returns:
            str: Time from the string.
        """

        time_reg = re.search(r"(\d+-){2}\d+ (\d+:){2}\d+", self.line).group(0)
        time = datetime.strptime(time_reg, "%y-%m-%d %H:%M:%S")
        return time

    def _get_ip(self, *args, **kwargs):
        """The function returns the value of the IP address from the string.

        Returns:
            str: IP address from the string.
        """

        ip_reg = re.search(r"ip=(\d+.){3}\d+", self.line).group(0)
        ip = re.sub(r"ip=", "", ip_reg)
        return ip

    def _get_mac(self, *args, **kwargs):
        """The function returns the value of the mac address from the string.

        Returns:
            str: MAC address from the string.
        """

        mac_reg = re.search(r"mac=\S+", self.line).group(0)
        mac = re.sub(r"mac=", "", mac_reg)
        return mac

    # endregion

    # region get string representation
    def get_sql_values(self, *args, **kwargs):
        """The function returns the values to be written to the sql database.

        Returns:
            str: values to be written to the sql database.
        """

        return "({}, '{}', '{}', '{}')".format(
            self.main_id, str(self.time), self.mac, self.line
        )

    def __str__(self, *args, **kwargs):
        """The function returns a string representation of an instance of the class.

        Returns:
            str: String representation of an instance of the class.
        """

        return "Time: {}, IP: {}".format(self.time, self.ip)

    # endregion
