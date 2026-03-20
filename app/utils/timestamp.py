from datetime import datetime, timezone

# def time_now():
#     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def time_now():
    return datetime.now(timezone.utc)