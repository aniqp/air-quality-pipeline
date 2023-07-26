import requests

def get_data():
  url = "https://api.openaq.org/v2/latest?limit=100&page=1&offset=0&sort=desc&parameter=pm25&radius=1000&city=ONTARIO&order_by=lastUpdated&dumpRaw=false"
  headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"}:
  response = requests.get(url, headers=headers)
  data = response.json()

  results = data['results']

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

def backfill_data(start_date, end_date):
  url = f"https://api.openaq.org/v2/measurements?date_from={start_date}&date_to={end_date}&limit=1000&parameter=pm25&location=Kitchener"
  headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"}

  response = requests.get(url, headers=headers)
  data = response.json()

  results = data['results']

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
    