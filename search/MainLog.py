from .InitializationError import InitializationError
from datetime import datetime, timedelta
from .Config import BaseConfig
from .DHCP2RAD import DHCP2RAD
from .DHCP import DHCP
import re

class MainLog:
    def __init__(self, line):
        if re.search(r'Context:.*?;inIP:.*?;Err:.*?;', line) is None:
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

    #region get content from line

    def _get_time(self):
        year = datetime.now().year + " "
        date_reg = re.search(r'\d+_\d+_', self.line).group(0) + year
        date = re.sub("_", '-', date_reg)
        time_reg = re.search(r'.*?\s', self.line).group(0)
        time = datetime.strptime(date + re.search(r'\d+:\d+:\d+', time_reg).group(0), "%d-%m-%Y %H:%M:%S")
        return time

    def _get_context(self):
        context_reg = re.search(r'Context:.*?;', self.line).group(0)
        context = re.sub(r'^Context: |;$', "", context_reg)
        return "'{}'".format(context) if context != "" else "null"
    
    def _get_ip(self):
        inip_reg = re.search(r'inIP:.*?;', self.line).group(0)
        inip = re.sub(r'^inIP: |;$', "", inip_reg)
        return inip

    def _get_error(self):
        error_reg = re.search(r'Err:.*?;', self.line).group(0)
        error = re.sub(r'^Err: |;$', "", error_reg)
        return error

    #endregion

    def _add_dhcp_instance(self, instance, with_time_delta=False):
        if with_time_delta:
            min_time = instance.time - timedelta(seconds=BaseConfig.DELAY_RANGE)
            max_time = instance.time + timedelta(seconds=BaseConfig.DELAY_RANGE)
            if min_time < self.time < max_time and self.ip == instance.ip:
                self.answer.append(instance)
            return
        self.answer.append(instance)

    def get_sql_value(self):
        return "({}, {}, '{}')".format(self.ip_id, self.context, str(self.time))

    def __str__(self):
        payload = 'Time: {}, IP: {}, Context: {}\n'.format(self.time.time(), self.ip, self.context)
        payload += "Other logs:\n"
        for instance in self.answer:
            payload += '\t{}\n'.format(instance)
        return payload

    def __add__(self, value):
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

