import pandas as pd
import requests
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
gcp_cloud_storage_bucket_block = GcsBucket.load("world-bank-bucket-block")


@task
def fetch_gdp_data(country: str, indicator: str, per_page: int = 100) -> list:
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page={per_page}"
    response = requests.get(url)
    data = response.json()
    print(data)
    return data


@task
def process_data(data: list) -> pd.DataFrame:
    if isinstance(data, list) and len(data) > 1:
        records = data[1]
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
        return df
    else:
        raise ValueError("No data returned or incorrect format.")


@task
def save_to_csv(df: pd.DataFrame) -> str:
    today = pd.Timestamp.now().normalize()
    today_date = today.strftime("%m%d%y")
    f"/tmp/gdp_data_{today_date}.csv"
    df.to_csv(filename, index=False)
    return filename


@flow
def gdp_pipeline(country: str = "US", indicator: str = "NY.GDP.MKTP.CD"):
    raw_data = fetch_gdp_data(country, indicator)
    df = process_data(raw_data)
    filename = save_to_csv(df)
    print(f"Data saved to {filename}")
    print(df.head())
