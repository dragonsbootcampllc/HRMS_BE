from datetime import datetime, timezone

def parse_datetime_with_utc_timezone(datetime_str):
    try:
        # Try parsing datetime string with timezone info
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")
    except ValueError:
        try:
            # Try parsing datetime string without timezone info
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Try parsing datetime string without timezone info and time
                datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Unsupported datetime format")

    # If the parsed datetime object has no timezone info, assume UTC
    if datetime_obj.tzinfo is None:
        datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
    else:
        # If the parsed datetime object has timezone info, convert it to UTC
        datetime_obj = datetime_obj.astimezone(timezone.utc)

    return datetime_obj