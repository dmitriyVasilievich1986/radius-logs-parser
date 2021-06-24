from .InitializationError import InitializationError
from datetime import datetime, timedelta
import re

class DHCP:
    def __init__(self, line):
        if re.search(r'DHCPACK', line) is None:
            raise InitializationError()
        self.main_id = None
        self.line = line

        self.device = self._get_device()
        self.time = self._get_time()
        self.mac = self._get_mac()
        self.ip = self._get_ip()
        self.difference = None

    def _get_mac(self):
        mac_re = re.search(r'(\S+:){5}\S+', self.line)
        return mac_re.group(0) if mac_re else "null"

    def _get_device(self):
        dev_re = re.search(r'\(.*?\)', self.line)
        return re.sub(r"\(|\)|\'|\`", '', dev_re.group(0)) if dev_re else "null"

    def _get_time(self):
        time_reg = re.search(r'[A-Z]+[a-z]+ \d+ .*?\s', self.line)
        if time_reg is None:
            raise InitializationError()
        date = "21 " + re.search(r'^[A-Z]+[a-z]+ \d+', time_reg.group(0)).group(0) + " "
        time = datetime.strptime(date + re.search(r'\d+:\d+:\d+', time_reg.group(0)).group(0), "%y %b %d %H:%M:%S")
        return time

    def _get_ip(self):
        ip_reg = re.search(r"on (\d+\.){3}\d+|for (\d+\.){3}\d+", self.line)
        if ip_reg is None:
            raise InitializationError()
        ip = re.sub(r"on |for ", "", ip_reg.group(0))
        return ip

    def get_sql_values(self):
        return "({}, '{}', '{}', '{}', '{}')".format(self.main_id, str(self.time), self.mac, self.device, re.sub(r"\'|\`", "", self.line))

    def __str__(self):
        return 'Time: {}, Difference: {}, MAC: {}, Device: {}'.format(self.time.time(), self.difference, self.mac, self.device)