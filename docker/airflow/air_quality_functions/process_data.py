from datetime import datetime, time, timedelta

def map_column_to_hour(col):
    hour_mapping = {
        f'H{i:02d}': f'{i:02d}:00'
        for i in range(24)
    }
    format_time = hour_mapping[col]
    new_time = datetime.strptime(format_time, '%H:%M').time()

    return new_time

def map_hour_to_column(hour):
    hour_mapping = {
        f'H{i:02d}': f'{i:02d}:00'
        for i in range(24)
    }
    format_time = hour_mapping[col]
    new_time = datetime.strptime(format_time, '%H:%M').time()

    return new_time

print(map_column_to_hour('H10'))