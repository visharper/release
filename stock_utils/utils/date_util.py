from datetime import datetime, timezone, timedelta

current_datetime_utc = datetime.utcnow()
current_datetime = datetime.now()
DEFAULT_FORMAT = "%Y-%m-%d"
YAHOO_DATE_FORMAT = "%Y-%m-%d %H:%M:%S%z"
DB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S%f"


def get_report_date(fmt="%y%m%d%H%M%S"):
    return current_datetime.strftime(fmt)


def get_today_date(fmt="%Y-%m-%d", utc: bool = False):
    if not utc:
        return current_datetime.strftime(fmt)
    return current_datetime_utc.strftime(fmt)


def get_today_dt():
    return datetime.date.today()


def get_tomorrow_date(fmt="%Y-%m-%d"):
    today_dt = get_today_dt
    return today_dt + timedelta(days=1)


def get_n_past_date(n: int, fmt=None):
    return_date = current_datetime + timedelta(days=n)
    if fmt:
        return return_date.strftime(fmt)
    return return_date


def add_microseconds(n: int, fmt=None, utc=False):
    if utc:
        return_date = current_datetime + timedelta(microseconds=n)
    return_date = current_datetime + timedelta(microseconds=n)
    if fmt:
        return return_date.strftime(fmt)
    return return_date


def dt_to_str(dt: datetime, fmt="%Y-%m-%d"):
    return dt.strftime(fmt)


def convert_str_to_dt(dt: str, return_fmt: str = ""):
    """
    Converts Str to Date format and if Return format is present
    returns date in that format
    """
    for fmt in (YAHOO_DATE_FORMAT, DEFAULT_FORMAT, DB_DATE_FORMAT):
        try:
            converted_dt = datetime.strptime(dt, fmt)
            if return_fmt:
                return dt_to_str(convert_str_to_dt, return_fmt)
            return converted_dt
        except ValueError:
            pass
    raise ValueError("no valid date format found!!")
