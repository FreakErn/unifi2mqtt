import datetime


def str_to_bool(value):
    return str(value).lower() in ("1", "true", "yes", "on")


def timestamp_to_isoformat(timestamp):
    if timestamp is None:
        return None
    try:
        dt = datetime.datetime.fromtimestamp(float(timestamp))
        return dt.isoformat()
    except (ValueError, OSError, TypeError):
        return None
