from datetime import datetime, date, timedelta

current_datetime = datetime.now()
current_datetime_utc = datetime.utcnow()
DEFAULT_FORMAT = "%Y-%m-%d"
CREATE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def get_report_date(fmt="%y%m%d%H%M%S"):
    return current_datetime.strftime(fmt)


def get_today_date(fmt="%Y-%m-%d", utc: bool = True):
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


def dt_to_str(dt: datetime, fmt="%Y-%m-%d"):
    return dt.strftime(fmt)
