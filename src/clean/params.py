from pathlib import Path
import pandas as pd


def build_country_params(
    merged_csv_path: Path,
    min_years_inflation: int = 5,
    latest_year_only_for_levels: bool = True,
) -> pd.DataFrame:
    df = pd.read_csv(merged_csv_path)

    # Ensure numeric
    for col in ['inflation_cpi_pct', 'unemployment_pct', 'oop_health_pct']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Inflation statistics over history
    infl = (
        df.dropna(subset=['inflation_cpi_pct'])
          .groupby(['iso3c', 'country'], as_index=False)
          .agg(
              inflation_years=('inflation_cpi_pct', 'count'),
              inflation_mean=('inflation_cpi_pct', 'mean'),
              inflation_sd=('inflation_cpi_pct', 'std'),
          )
    )
    infl['inflation_sd'] = infl['inflation_sd'].fillna(0.0)
    infl = infl[infl['inflation_years'] >= min_years_inflation].copy()

    if latest_year_only_for_levels:
        unemp_last = (
            df.dropna(subset=['unemployment_pct'])
            .sort_values('year')
            .groupby(['iso3c', 'country'], as_index=False)
            .tail(1)[['iso3c', 'country', 'year', 'unemployment_pct']]
            .rename(columns={'year': 'unemp_year', 'unemployment_pct': 'unemployment_level'})
        )

        oop_last = (
            df.dropna(subset=['oop_health_pct'])
            .sort_values('year')
            .groupby(['iso3c', 'country'], as_index=False)
            .tail(1)[['iso3c', 'country', 'year', 'oop_health_pct']]
            .rename(columns={'year': 'oop_year', 'oop_health_pct': 'oop_health_level'})
        )

        levels = unemp_last.merge(oop_last, on=['iso3c', 'country'], how='outer')
        levels['levels_year'] = levels[['unemp_year', 'oop_year']].max(axis=1)
        levels = levels.drop(columns=['unemp_year', 'oop_year'])
    else:
        levels = (
            df.groupby(['iso3c', 'country'], as_index=False)
              .agg(
                  unemployment_level=('unemployment_pct', 'mean'),
                  oop_health_level=('oop_health_pct', 'mean'),
              )
        )
        levels['levels_year'] = pd.NA

    params = infl.merge(levels, on=['iso3c', 'country'], how='left')
    params['inflation_mean'] = params['inflation_mean'].clip(-50, 200)
    params['inflation_sd'] = params['inflation_sd'].clip(0, 100)
    params['unemployment_level'] = params['unemployment_level'].clip(0, 60)
    params['oop_health_level'] = params['oop_health_level'].clip(0, 100)
    params['data_ok'] = (
            params['unemployment_level'].notna() & params['oop_health_level'].notna()
    )
    params = params[params['data_ok']].copy()
    params = params.sort_values('country').reset_index(drop=True)
    return params


def save_country_params(params: pd.DataFrame, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    params.to_csv(out_path, index=False)
    return out_path
