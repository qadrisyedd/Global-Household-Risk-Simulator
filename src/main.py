'''
Name: Syed Qadri
Program: Global Household Risk
Covered Topics: Programming (Python, API), Actuarial Science, Quantitative Finance (Quants)
'''

from pathlib import Path
from clean.params import build_country_params, save_country_params
from ingest.worldbank import fetch_indicator
from clean.merge import merge_indicators, save_processed
import pandas as pd
from model.simulator import simulate_country
from model.metrics import compute_metrics, risk_score_0_100, quick_debug_summary
from viz.plots import plot_top_n, plot_score_hist, plot_top_n_cvar

INDICATORS = {
    'inflation_cpi_pct': 'FP.CPI.TOTL.ZG',
    'unemployment_pct': 'SL.UEM.TOTL.ZS',
    'oop_health_pct': 'SH.XPD.OOPC.CH.ZS',
}

START_YEAR = 2000
END_YEAR = 2024
REFRESH_DATA = False  # Change to TRUE if no data is available or to update data


def download(root: Path):
    raw_dir = root / 'data' / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name, code in INDICATORS.items():
        out_path = raw_dir / f'{name}_{START_YEAR}_{END_YEAR}.csv'

        if out_path.exists() and not REFRESH_DATA:
            print(f'✓ using cached {out_path.name}\n')
            continue

        print(f'↓ downloading {name} ({code})')
        df = fetch_indicator(code, START_YEAR, END_YEAR)
        df.to_csv(out_path, index=False)
        print(f'  saved: {out_path.name} | rows={len(df):,}\n')


def merge(root: Path):
    df = merge_indicators(root, START_YEAR, END_YEAR)
    out = save_processed(df, root, f'country_year_{START_YEAR}_{END_YEAR}.csv')


def parameters(root: Path):
    merged_path = root / 'data' / 'processed' / f'country_year_{START_YEAR}_{END_YEAR}.csv'
    params = build_country_params(merged_path, min_years_inflation=5)
    out_path = root / 'data' / 'processed' / f'country_params_{START_YEAR}_{END_YEAR}.csv'
    save_country_params(params, out_path)


def run_sim(root: Path):
    status = False  # Debugger, Change to True if you want to use it (I had it when I was building the program, it's a good tool)
    print('Running Monte Carlo simulations...')
    params_path = root / 'data' / 'processed' / f'country_params_{START_YEAR}_{END_YEAR}.csv'
    df = pd.read_csv(params_path)

    # Filter out World Bank aggregates (AGG) --> keeps real countries
    AGG = {
        'AFE', 'AFW', 'ARB', 'CEB', 'CSS', 'EAP', 'EAR', 'EAS', 'ECA', 'ECS', 'EMU', 'EUU', 'FCS', 
        'HIC', 'HPC', 'IBD', 'IBT', 'IDA', 'IDB', 'IDX', 'INX', 'LAC', 'LCN', 'LDC', 'LIC', 'LMC', 
        'LMY', 'LTE', 'MEA', 'MIC', 'MNA', 'NAC', 'OED', 'OSS', 'PRE', 'PSS', 'PST', 'SAS', 'SSA', 
        'SSF', 'SST', 'TEA', 'TEC', 'TLA', 'TMN', 'TSA', 'TSS', 'UMC', 'WLD'
    }
    df = df[~df['iso3c'].isin(AGG)].copy()

    results = []
    for _, row in df.iterrows():
        stressed, worst = simulate_country(
            inflation_mean_annual=row['inflation_mean'],
            inflation_sd_annual=row['inflation_sd'],
            unemployment_pct=row['unemployment_level'],
            oop_health_pct=row['oop_health_level'],
            n_sims=3000,
            horizon_months=12,
            seed=42
        )

        m = compute_metrics(stressed, worst)

        results.append({
            'iso3c': row['iso3c'],
            'country': row['country'],
            'stress_probability': m['stress_probability'],
            'severe_stress_probability': m['severe_stress_probability'],
            'avg_shortfall_when_stressed': m['avg_shortfall_when_stressed'],
            'var95_shortfall': m['var95_shortfall'],
            'cvar95_shortfall': m['cvar95_shortfall'],
        })

    out_df = pd.DataFrame(results)

    # Percentiles
    p90_severe = float(out_df['severe_stress_probability'].quantile(0.90))
    p90_avg = float(out_df['avg_shortfall_when_stressed'].quantile(0.90))
    p90_cvar = float(out_df['cvar95_shortfall'].quantile(0.90))
    scores = []
    for _, r in out_df.iterrows():
        scores.append(
            risk_score_0_100(
                r['severe_stress_probability'],
                r['avg_shortfall_when_stressed'],
                r['cvar95_shortfall'],
                p90_severe,
                p90_avg,
                p90_cvar,
            )
        )
    out_df['risk_score'] = scores
    out_df = out_df.sort_values('risk_score', ascending=False)

    # Optional debug print (comment below line if not wanted)
    quick_debug_summary(out_df, status)

    out_path = root / 'data' / 'processed' / f'risk_results_{START_YEAR}_{END_YEAR}.csv'
    out_df.to_csv(out_path, index=False)


def create_plots(root: Path):
    print('\nGenerating plots...')

    out_dir = root / 'data' / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('\nPlots now available!')


def main():
    root = Path(__file__).resolve().parents[1]
    download(root)
    merge(root)
    parameters(root)
    run_sim(root)
    create_plots(root)


if __name__ == '__main__':
    main()
