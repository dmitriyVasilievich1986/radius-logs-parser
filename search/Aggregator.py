from sre_constants import IN_IGNORE
from .InitializationError import InitializationError
from datetime import datetime, timedelta
from collections import OrderedDict
from .Config import BaseConfig, V3
from .DHCP2RAD import DHCP2RAD
from .MainLog import MainLog
from .DHCP import DHCP
from .DB import DB

class Aggregator:
    def __init__(self, context="full", time=600, ip_address=None, black_list=False):
        self.ip_address = ip_address or list()
        self.black_list = black_list
        self.logs = OrderedDict()
        self.context = context
        self.logs_count = 1
        self.time = time

    def _get_values(self):
        payload = list()
        for x in list(self.logs.values()):
            payload += x
        return payload

    def __add__(self, value):
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

    def _add_main_log_instance(self, instance):
        if self.context == "context" and instance.context == 'null':
            raise InitializationError()
        if self.context == "null" and instance.context != 'null':
            raise InitializationError()
        if (instance.ip not in self.ip_address and self.black_list) or (instance.ip in self.ip_address and not self.black_list):
            raise InitializationError()
        if self.logs.get(instance.ip, False):
            instance.ip_id = self.logs[instance.ip][0].ip_id
            self.logs[instance.ip].append(instance)
        else:
            instance.ip_id = self.logs_count
            self.logs_count += 1
            self.logs[instance.ip] = [instance]

    def _add_dhcp_instance(self, instance):
        # min_time = instance.time - timedelta(seconds=self.time)
        max_time = instance.time + timedelta(seconds=self.time)
        data = self.logs.get(instance.ip, [])
        filtered_data = filter(lambda x:instance.time <= x.time < max_time, data)
        for main_log in filtered_data:
            main_log + instance

    def __str__(self, filtered_list=None, n=None):
        filtered_list = filtered_list or self._get_values()
        n = n and min(n, len(filtered_list)) or len(filtered_list)
        payload = ""
        for main_log in filtered_list[:n]:
            payload += str(main_log)
        payload += "Show: {}, Overall: {}".format(n, len(filtered_list))
        return payload

    def _get_only_with_answer(self):
        filtered = list(filter(lambda x: x.full, self._get_values()))
        return filtered

    def show(self, only_answered=False, n=5):
        if only_answered:
            filtered = self._get_only_with_answer()
            return self.__str__(filtered_list=filtered, n=n) if len(filtered) else "Matches not found"
        else:
            return self.__str__(n=n)

    def save_sqlite(self):
        db = DB()
        self._insert_ip(db)
        self._insert_main(db)
        db.close()

    def _insert_ip(self, db):
        values = ",".join("('{}')".format(x) for x in list(self.logs.keys()))
        query = "INSERT INTO ip('ip') VALUES {};".format(values)
        db.execute(query)

    def _insert_main(self, db):
        mains_null, mains_full, dhcp, dhcp2rad = self._get_all_mains_and_dhcp()
        if len(mains_full):
            values = ",".join(x.get_sql_value() for x in mains_full)
            query = "INSERT INTO main('ip_id', 'context', 'time') VALUES {};".format(values)
            db.execute(query)
        if len(dhcp):
            values = ",".join(x.get_sql_values() for x in dhcp)
            query = "INSERT INTO dhcp('main_id', 'time', 'mac', 'device', 'text') VALUES {};".format(values)
            db.execute(query)
        if len(dhcp2rad):
            values = ",".join(x.get_sql_values() for x in dhcp2rad)
            query = "INSERT INTO dhcp2rad('main_id', 'time', 'mac', 'text') VALUES {};".format(values)
            db.execute(query)
        if len(mains_null):
            values = ",".join(x.get_sql_value() for x in mains_null)
            query = "INSERT INTO main('ip_id', 'context', 'time') VALUES {};".format(values)
            db.execute(query)

    def _get_all_dhcp(self, mains):
        payload = list()
        for m in mains:
            payload += m.answer
        return payload

    def _get_all_mains_and_dhcp(self):
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
        # print(dhcp)
        return mains_null, mains_full, dhcp, dhcp2rad
