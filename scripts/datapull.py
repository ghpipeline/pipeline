import pandas as pd
import requests

import requests
import pandas as pd

# Example: GDP (current US$) for United States
indicator = "NY.GDP.MKTP.CD"
country = "US"
url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=100"

response = requests.get(url)
data = response.json()

# Check if response is structured correctly
if isinstance(data, list) and len(data) > 1:
    records = data[1]
    
    # Extract relevant fields
    df = pd.DataFrame([{
        "country": item['country']['value'],
        "indicator": item['indicator']['value'],
        "value": item['value'],
        "date": item['date'],
        "unit": item.get('unit', None),
        "obs_status": item.get('obs_status', None)
    } for item in records if item['value'] is not None])
    
    df['value'] = df['value'].astype(float)
    df = df.sort_values(by='date', ascending=False)

    print(df.head())
else:
    print("No data returned or incorrect format.")





