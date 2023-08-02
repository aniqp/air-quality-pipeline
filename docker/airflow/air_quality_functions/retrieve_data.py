import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests
from air_quality_functions.process_data import map_column_to_hour, map_hour_to_column, process_utc_string
from datetime import date, time, datetime

def get_data():
  url = "https://api.openaq.org/v2/latest?parameter=pm25&parameter=o3&location=Kitchener&order_by=lastUpdated"
  headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"}
  response = requests.get(url, headers=headers)
  data = response.json()
  print(f'Data: {data}')

  try:
    results = data['results']
  except KeyError:
    print('API failed to retrieve data.')

  measurements = results[0]['measurements']

  params = {'pm25':
              {'value':0,
              'last_updated':0}
            ,'o3':
              {'value':0,
                'last_updated':0}
              }

  for measurement in measurements:
      parameter = measurement['parameter']
      if parameter in params.keys():
          params[parameter]['value'] = measurement['value']
          params[parameter]['last_updated'] = measurement['lastUpdated']

  return params

def backfill_data(start_date, curr_datetime):
    def index_time_data(mytime):
        time_to_column_index = {}
        for hour in range(24):
            time_obj = time(hour=hour)
            time_to_column_index[time_obj] = hour
        return time_to_column_index[mytime] + 1

    url = f"https://api.openaq.org/v2/measurements?date_from={start_date}&limit=10000&parameter=pm25&parameter=o3&location=Kitchener&order_by=datetime"
    headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"}

    response = requests.get(url, headers=headers)
    data = response.json()

    try:
      results = data['results']
    except KeyError:
       print('API failed to retrieve data.')

    pm25_data = []
    o3_data = []

    row = [None for i in range(24)]
    row.insert(0, start_date)

    prev_date = None

    for current_result in results:
      if current_result['parameter'] == 'pm25':
          datetime = process_utc_string(current_result['date']['utc'])
          if datetime > curr_datetime:
            check_if_none = sum([i is not None for i in row[1:]])
            if prev_date is not None and prev_date != datetime.date():
                if check_if_none != 0:
                  pm25_data.append(tuple(row))  # Convert row to a tuple before appending
                row = [None for i in range(24)]
                row.insert(0, str(datetime.date()))

            row[index_time_data(datetime.time())] = str(current_result['value'])

          prev_date = datetime.date()

    # Append the last row outside the loop
    pm25_data.append(tuple(row))  # Convert row to a tuple before appending

    return pm25_data

    # return results
    
# start_date = '2023-07-19'
# curr_datetime = datetime.combine(datetime(2023, 7, 31), time(2, 0))
# print(backfill_data(str(datetime(2023,7,31).date()), curr_datetime))


print(get_data())