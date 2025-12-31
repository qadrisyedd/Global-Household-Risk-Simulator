import numpy as np


def simulate_country(
    inflation_mean_annual: float,
    inflation_sd_annual: float,
    unemployment_pct: float,
    oop_health_pct: float,
    n_sims: int = 5000,
    horizon_months: int = 12,
    seed: int | None = None,
):

    '''
    Monte Carlo simulation of household financial stress for one country.

    this program assumes:
    - A household has monthly income and expenses, inflation raises variable expenses
    - Job shock happens with its probability linked to unemployment_pct from data
    - Health shock severity scales with data from oop_health_pct

    Returns:
    - stressed_any: (n_sims,) boolean (True if stress occurred at least once over the horizon)
    - worst_shortfall: (n_sims,) maximum monthly shortfall observed over the horizon (0 if never stressed)
    '''

    rng = np.random.default_rng(seed)

    # Household baseline
    monthly_income = 3000.0
    fixed_expenses = 1200.0
    variable_expenses = 1200.0
    savings = 3000.0  # buffer used to cover deficits

    # Inflation: annual
    mu_m = inflation_mean_annual / 12.0
    sd_m = inflation_sd_annual / np.sqrt(12.0)

    # Job event
    p_job = np.clip((unemployment_pct / 100.0) / 12.0 * 2.0, 0.0, 0.25)

    # Health event
    p_health = 0.06  # 6% chance per month
    base_health_cost = 500.0
    health_multiplier = 0.5 + (oop_health_pct / 100.0)  # ~0.5 to 1.5

    stressed_any = np.zeros(n_sims, dtype=bool)
    worst_shortfall = np.zeros(n_sims, dtype=float)

    for i in range(n_sims):
        cash = savings
        var_cost = variable_expenses
        worst = 0.0
        stressed = False

        for _ in range(horizon_months):
            # Inflation
            infl = rng.normal(mu_m, sd_m)
            infl = np.clip(infl, -0.05, 0.20)  # -5% to +20% monthly
            var_cost *= (1.0 + infl)

            # Income + job event
            income = monthly_income
            if rng.random() < p_job:
                income *= 0.65  # 35% drop

            # Health event
            health_cost = 0.0
            if rng.random() < p_health:
                health_cost = base_health_cost * health_multiplier * rng.lognormal(mean=0.0, sigma=0.6)

            expenses = fixed_expenses + var_cost + health_cost
            shortfall = max(0.0, expenses - income)

            if shortfall > 0:
                stressed = True
                worst = max(worst, shortfall)
                cash -= shortfall
                if cash < 0:
                    # once savings < 0 we treat it as severe stress, program goes on (lol)
                    cash = 0.0

        stressed_any[i] = stressed
        worst_shortfall[i] = worst

    return stressed_any, worst_shortfall
