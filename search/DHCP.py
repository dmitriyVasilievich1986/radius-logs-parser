from .InitializationError import InitializationError
from datetime import datetime
import re


class DHCP:
    # region class initialization
    def __init__(self, line, *args, **kwargs):
        """Class for processing and storing data from the dhcp log.

        Args:
            line (str): String line from dhcp log.

        Raises:
            InitializationError: If the string does not match the pattern, an error is thrown.
        """

        if re.search(r"DHCPACK", line) is None:
            raise InitializationError()
        self.main_id = None
        self.line = line

        self.device = self._get_device()
        self.time = self._get_time()
        self.mac = self._get_mac()
        self.ip = self._get_ip()
        self.difference = None

    # endregion

    # region get parsed data from line from log
    def _get_mac(self, *args, **kwargs):
        """The function returns the value of the mac address from the string.

        Returns:
            str: MAC address from the string.
        """

        mac_re = re.search(r"(\S+:){5}\S+", self.line)
        return mac_re.group(0) if mac_re else "null"

    def _get_device(self, *args, **kwargs):
        """The function returns the value of the device from the string.

        Returns:
            str: Device from the string.
        """

        dev_re = re.search(r"\(.*?\)", self.line)
        return re.sub(r"\(|\)|\'|\`", "", dev_re.group(0)) if dev_re else "null"

    def _get_time(self, *args, **kwargs):
        """The function returns the value of the time from the string.

        Returns:
            str: Time from the string.
        """

        time_reg = re.search(r"[A-Z]+[a-z]+ \d+ .*?\s", self.line)
        if time_reg is None:
            raise InitializationError()
        date = "21 " + re.search(r"^[A-Z]+[a-z]+ \d+", time_reg.group(0)).group(0) + " "
        time = datetime.strptime(
            date + re.search(r"\d+:\d+:\d+", time_reg.group(0)).group(0),
            "%y %b %d %H:%M:%S",
        )
        return time

    def _get_ip(self, *args, **kwargs):
        """The function returns the value of the IP address from the string.

        Returns:
            str: IP address from the string.
        """

        ip_reg = re.search(r"on (\d+\.){3}\d+|for (\d+\.){3}\d+", self.line)
        if ip_reg is None:
            raise InitializationError()
        ip = re.sub(r"on |for ", "", ip_reg.group(0))
        return ip

    # endregion

    # region get string representation
    def get_sql_values(self, *args, **kwargs):
        """The function returns the values to be written to the sql database.

        Returns:
            str: values to be written to the sql database.
        """

        return "({}, '{}', '{}', '{}', '{}')".format(
            self.main_id,
            str(self.time),
            self.mac,
            self.device,
            re.sub(r"\'|\`", "", self.line),
        )

    def __str__(self, *args, **kwargs):
        """The function returns a string representation of an instance of the class.

        Returns:
            str: String representation of an instance of the class.
        """

        return "Time: {}, Difference: {}, MAC: {}, Device: {}".format(
            self.time.time(), self.difference, self.mac, self.device
        )

    # endregion
