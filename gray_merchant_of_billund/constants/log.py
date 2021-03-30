from gray_merchant_of_billund.constants.gmob import (
    APPLICATION_NAME,
    RESOURCES_DIR,
)
from gray_merchant_of_billund.utils.path import posix_path

DEFAULT_LOG_FORMAT = (
    "%(levelname)s:%(asctime)s:%(module)s:%(funcName)s:"
    "L%(lineno)d: %(message)s"
)
DEFAULT_LOGGING_FILE = posix_path(RESOURCES_DIR, f"{APPLICATION_NAME}.log")
