import logging
from pathlib import Path

from gray_merchant_of_billund.constants.gmob import APPLICATION_NAME
from gray_merchant_of_billund.constants.log import (
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOGGING_FILE,
)


def get_logger(
    name=APPLICATION_NAME,
    log_format=DEFAULT_LOG_FORMAT,
    stdout_level=logging.INFO,
    file_name=DEFAULT_LOGGING_FILE,
    file_level=logging.INFO,
):
    Path(file_name).parent.mkdir(exist_ok=True)
    Path(file_name).touch(exist_ok=True)
    logging.basicConfig(level=stdout_level, format=log_format)
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    return logger
