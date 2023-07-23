import requests
import json
import pandas as pd

url = "https://api.openaq.org/v2/measurements?date_from=2023-07-17&date_to=2023-07-18&limit=20000&page=1&offset=0&sort=desc&radius=1000&location=Kitchener&order_by=datetime"

headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"}

response = requests.get(url, headers=headers)

data = response.json()

results = data['results']

df = pd.DataFrame(results)

with open('historical_data_2023.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)