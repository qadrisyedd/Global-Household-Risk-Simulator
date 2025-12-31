import numpy as np


def compute_metrics(stressed_any: np.ndarray, worst_shortfall: np.ndarray) -> dict:
    stress_prob = float(np.mean(stressed_any))
    severe_stress_prob = float(np.mean(worst_shortfall > 1500))
    stressed_shortfalls = worst_shortfall[worst_shortfall > 0]
    if stressed_shortfalls.size == 0:
        avg_shortfall = 0.0
        var95 = 0.0
        cvar95 = 0.0
    else:
        avg_shortfall = float(np.mean(stressed_shortfalls))
        var95 = float(np.quantile(stressed_shortfalls, 0.95))
        cvar95 = float(np.mean(stressed_shortfalls[stressed_shortfalls >= var95]))
    return {
        'stress_probability': stress_prob,
        'severe_stress_probability': severe_stress_prob,
        'avg_shortfall_when_stressed': avg_shortfall,
        'var95_shortfall': var95,
        'cvar95_shortfall': cvar95,
    }


def risk_score_0_100(
    severe_stress_prob: float,
    avg_shortfall: float,
    cvar95: float,
    p90_severe: float,
    p90_avg: float,
    p90_cvar: float,
) -> float:
    sev_prob_component = np.clip(severe_stress_prob / max(p90_severe, 1e-6), 0, 1)
    avg_component = np.clip(avg_shortfall / max(p90_avg, 1e-6), 0, 1)
    tail_component = np.clip(cvar95 / max(p90_cvar, 1e-6), 0, 1)
    score = 100.0 * (0.2 * sev_prob_component + 0.3 * avg_component + 0.5 * tail_component)
    return float(np.clip(score, 0, 100))


def quick_debug_summary(df, status):
    if status:
        print('\nDEBUG: Risk metric summary')
        cols = [
            'stress_probability',
            'severe_stress_probability',
            'avg_shortfall_when_stressed',
            'cvar95_shortfall',
            'risk_score',
        ]
        print(df[cols].describe(percentiles=[0.5, 0.9, 0.95, 0.99]))
    else:
        return
