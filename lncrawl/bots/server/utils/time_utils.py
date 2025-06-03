from datetime import datetime
from typing import Any

from dateutil import parser
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc


def current_timestamp():
    '''Current UNIX timestamp in milliseconds'''
    return round(1000 * datetime.now().timestamp())


def as_unix_time(time: Any) -> int | None:
    try:
        if isinstance(time, int):
            return time
        if isinstance(time, str):
            time = parser.parse(time)
        if isinstance(time, datetime):
            return round(1000 * time.timestamp())
    except Exception:
        pass
    return None


def time_from_now(
    years=0, months=0, days=0, weeks=0,
    hours=0, minutes=0, seconds=0
) -> datetime:
    delta = relativedelta(
        years=years, months=months, days=days, weeks=weeks,
        hours=hours, minutes=minutes, seconds=seconds
    )
    return datetime.now(tzutc()).replace(microsecond=0) + delta
