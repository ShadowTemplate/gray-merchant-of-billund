import time
from datetime import datetime

from gray_merchant_of_billund.constants.gmob import DEFAULT_DATE_FORMAT

SECOND = 1000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY
YEAR = 365 * DAY


def now() -> int:
    return int(round(time.time() * 1000))


def pretty_str(now_ms: int, date_format=DEFAULT_DATE_FORMAT) -> str:
    now_dt = datetime.fromtimestamp(now_ms / 1000.0)
    return now_dt.strftime(date_format)
