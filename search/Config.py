import logging
import sys

V3 = sys.version_info.major == 3


class MyFormatter(logging.Formatter):
    _formats = {
        "INFO": logging.Formatter(
            "\033[92m[%(asctime)s]%(levelname)s: %(message)s\033[0m", datefmt="%H:%M:%S"
        ),
        "ERROR": logging.Formatter(
            "\033[91m[%(asctime)s]%(levelname)s: %(message)s\033[0m", datefmt="%H:%M:%S"
        ),
        "WARNING": logging.Formatter(
            "\033[93m[%(asctime)s]%(levelname)s: %(message)s\033[0m", datefmt="%H:%M:%S"
        ),
    }

    def __init__(self, *args, **kwargs):
        if V3:
            super().__init__(*args, **kwargs)
        else:
            super(MyFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        f = self._formats.get(record.levelname)

        return f.format(record)


logger = logging.getLogger()

formatter = MyFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class BaseConfig:
    DELAY_RANGE = 600
    CONTEXT = ["full", "context", "null"]
    LOGS = "logs/06_14"
