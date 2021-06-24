import sys

V3 = sys.version_info.major == 3

class BaseConfig:
    DELAY_RANGE = 600
    CONTEXT = ["full", "context", "null"]
    LOGS = [
        #"logs/web_07_06.log",
        # "logs/web_08_06.log",
        "logs/web_16.log",
        #"logs/d2r_06_07.log",
        #  "logs/t.log",
        #  "logs/dhcpd_14_06.log",
        #  "logs/d2r.log",
        # "logs/l2.log",
        # "logs/sum_logs.log",
        # "logs/dhcp_30_05.log",
        # "logs/dhcp_head250000.log",
    ]
