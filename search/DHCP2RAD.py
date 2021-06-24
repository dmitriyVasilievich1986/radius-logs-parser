from .InitializationError import InitializationError
import re
from datetime import datetime

class DHCP2RAD:
    def __init__(self, line):
        if re.search(r'Response', line) is None:
            raise InitializationError()
        self.main_id = None
        self.line = line

        self.time = self._get_time()
        self.mac = self._get_mac()
        self.ip = self._get_ip()

    def _get_time(self):
        time_reg = re.search(r'(\d+-){2}\d+ (\d+:){2}\d+', self.line).group(0)
        time = datetime.strptime(time_reg, "%y-%m-%d %H:%M:%S")
        return time

    def _get_ip(self):
        ip_reg = re.search(r"ip=(\d+.){3}\d+", self.line).group(0)
        ip = re.sub(r"ip=", "", ip_reg)
        return ip

    def _get_mac(self):
        mac_reg = re.search(r"mac=\S+", self.line).group(0)
        mac = re.sub(r"mac=", "", mac_reg)
        return mac

    def get_sql_values(self):
        return "({}, '{}', '{}', '{}')".format(self.main_id, str(self.time), self.mac, self.line)

    def __str__(self):
        return "Time: {}, IP: {}".format(self.time, self.ip)