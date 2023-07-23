import requests

def get_data(url, headers):
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