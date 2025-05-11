# simulation.py
import numpy as np
import pandas as pd
from config import (SEED, START_DATE, END_DATE, DATA_PATH, COUNTRIES,
                    TARGET_RMSE, BIAS_FRACTION, NUM_SCENARIOS)

def simulate_forecast():
    rng = np.random.default_rng(SEED)

    df = pd.read_csv(DATA_PATH, parse_dates=['Datetime (UTC)'])
    price_df = (
        df.pivot(index='Datetime (UTC)', columns='Country', values='Price (EUR/MWhe)')
          .loc[:, COUNTRIES]
          .sort_index()
    )
    sim_df = price_df.loc[START_DATE:END_DATE]
    T, M = sim_df.shape

    bias = BIAS_FRACTION * TARGET_RMSE
    sigma_noise = (TARGET_RMSE**2 - bias**2)**0.5
    base = sim_df.values[..., None] + bias
    scenarios = rng.normal(base, sigma_noise, (T, M, NUM_SCENARIOS))

    mu_df = pd.DataFrame(scenarios.mean(axis=2), index=sim_df.index, columns=COUNTRIES)
    sigma_df = pd.DataFrame(scenarios.std(axis=2), index=sim_df.index, columns=COUNTRIES)

    return mu_df, sigma_df, sim_df, COUNTRIES, T
