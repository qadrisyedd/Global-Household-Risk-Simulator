from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_top_n(out_dir: Path, results_csv: Path, n: int = 20):
    df = pd.read_csv(results_csv)
    df = df.sort_values('risk_score', ascending=False).head(n)

    plt.figure()
    plt.barh(df['country'], df['cvar95_shortfall'])
    plt.gca().invert_yaxis()
    plt.xlabel('CVaR95 Shortfall ($)')
    plt.title(f'Top {n} Countries by Risk Score (bars show tail shortfall)')
    plt.tight_layout()

    out_path = out_dir / f'top_{n}_stress_probability.png'
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path


def plot_top_n_cvar(out_dir: Path, results_csv: Path, n: int = 20):
    df = pd.read_csv(results_csv)
    df = df.sort_values('risk_score', ascending=False).head(n)

    plt.figure()
    plt.barh(df['country'], df['cvar95_shortfall'])
    plt.gca().invert_yaxis()
    plt.xlabel('CVaR95 Shortfall ($)')
    plt.title(f'Top {n} Countries by Risk Score (bars show tail shortfall)')
    plt.tight_layout()

    out_path = out_dir / f'top_{n}_cvar95_shortfall.png'
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path


def plot_score_hist(out_dir: Path, results_csv: Path):
    df = pd.read_csv(results_csv)

    plt.figure()
    plt.hist(df['risk_score'].dropna(), bins=30)
    plt.xlabel('Risk Score (0–100)')
    plt.ylabel('Number of Countries')
    plt.title('Distribution of Risk Scores')
    plt.tight_layout()

    out_path = out_dir / 'risk_score_distribution.png'
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path
