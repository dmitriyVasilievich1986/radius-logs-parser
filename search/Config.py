import logging
import sys

V3 = sys.version_info.major == 3


logging.basicConfig(
    format="[%(asctime)s]%(levelname)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger()


class BaseConfig:
    DELAY_RANGE = 600
    CONTEXT = ["full", "context", "null"]
    LOGS = "logs/06_14"
