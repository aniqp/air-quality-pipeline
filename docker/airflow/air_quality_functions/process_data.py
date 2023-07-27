import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, time, timedelta, timezone
from dateutil.parser import parse

def map_column_to_hour(col):
    hour_mapping = {
        f'H{i:02d}': f'{i:02d}:00'
        for i in range(24)
    }
    format_time = hour_mapping[col]
    new_time = datetime.strptime(format_time, '%H:%M').time()

    return new_time

def map_hour_to_column(hour):
    hour_str = hour.strftime('%H:%M')
    hour_mapping = {
        f'{i:02d}:00': f'H{i:02d}'
        for i in range(24)
    }
    new_time = hour_mapping[hour_str]

    return new_time

def process_utc_string(utc):
    utc_datetime = parse(utc).astimezone(timezone.utc)
    formatted_datetime_str = utc_datetime.strftime("%Y-%m-%d %H:%M")
    new_datetime = datetime.strptime(formatted_datetime_str, "%Y-%m-%d %H:%M")

    return new_datetime