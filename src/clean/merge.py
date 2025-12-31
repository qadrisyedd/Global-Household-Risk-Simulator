from pathlib import Path
import pandas as pd


def load_raw_csv(root: Path, filename: str) -> pd.DataFrame:
    path = root / 'data' / 'raw' / filename
    df = pd.read_csv(path)
    df['year'] = df['year'].astype(int)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df


def merge_indicators(root: Path, start_year: int, end_year: int) -> pd.DataFrame:
    inf = load_raw_csv(root, f'inflation_cpi_pct_{start_year}_{end_year}.csv').rename(
        columns={'value': 'inflation_cpi_pct'}
    )
    unemp = load_raw_csv(root, f'unemployment_pct_{start_year}_{end_year}.csv').rename(
        columns={'value': 'unemployment_pct'}
    )
    oop = load_raw_csv(root, f'oop_health_pct_{start_year}_{end_year}.csv').rename(
        columns={'value': 'oop_health_pct'}
    )

    keys = ['iso3c', 'country', 'year']
    df = inf.merge(unemp[keys + ['unemployment_pct']], on=keys, how='outer')
    df = df.merge(oop[keys + ['oop_health_pct']], on=keys, how='outer')
    df = df.sort_values(['country', 'year']).reset_index(drop=True)
    return df


def save_processed(df: pd.DataFrame, root: Path, filename: str) -> Path:
    out_path = root / 'data' / 'processed' / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path
