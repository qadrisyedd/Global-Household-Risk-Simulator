import requests
import pandas as pd

BASE = 'https://api.worldbank.org/v2'


def fetch_indicator(indicator_code: str, start_year: int, end_year: int) -> pd.DataFrame:
    page = 1
    records = []
    while True:
        url = (
            f'{BASE}/country/all/indicator/{indicator_code}'
            f'?format=json&per_page=20000&page={page}&date={start_year}:{end_year}'
        )
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2 or data[1] is None:
            break
        for row in data[1]:
            iso3 = row.get('countryiso3code')
            if not iso3:
                continue

            year = row.get('date')
            if year is None:
                continue

            records.append(
                {
                    'iso3c': iso3,
                    'country': (row.get('country') or {}).get('value'),
                    'year': int(year),
                    'value': row.get('value'),
                }
            )
        pages = data[0].get('pages', 1)
        if page >= pages:
            break
        page += 1
    return pd.DataFrame.from_records(records)
