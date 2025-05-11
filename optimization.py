
import pandas as pd
from pulp import (
    LpProblem, LpVariable, LpBinary, LpContinuous, LpMaximize,
    lpSum, value, LpStatus, PULP_CBC_CMD)
from config import SEED, BATTERY, RISK_AVERSION

def optimize_battery_DRO(mu_df: pd.DataFrame, sigma_df: pd.DataFrame,
                         params=BATTERY, risk=RISK_AVERSION):
    T, _ = mu_df.shape
    markets = list(mu_df.columns)
    prob = LpProblem("Battery_Arbitrage_DRO", LpMaximize)

    # decision vars
    x_plus = LpVariable.dicts('x_plus', (range(T), markets), 0, params.charge_rate, cat=LpContinuous)
    x_minus = LpVariable.dicts('x_minus', (range(T), markets), 0, params.charge_rate, cat=LpContinuous)
    z = LpVariable.dicts('z', (range(T), markets), cat=LpBinary)
    y = LpVariable.dicts('y', range(T), cat=LpBinary)
    soc = LpVariable.dicts(
        'soc', range(T+1),
        params.battery_capacity_buffer * params.battery_capacity,
        (1 - params.battery_capacity_buffer) * params.battery_capacity,
        cat=LpContinuous
    )

    prob += soc[0] == params.initial_soc

    for t in range(T):
        prob += soc[t+1] == (
            soc[t]
            - lpSum(x_plus[t][m]  for m in markets)
            + params.efficiency * lpSum(x_minus[t][m] for m in markets)
        )
        prob += lpSum(z[t][m] for m in markets) <= 1
        for m in markets:
            prob += x_plus[t][m] <= params.charge_rate * z[t][m]
            prob += x_minus[t][m] <= params.charge_rate * z[t][m]
            prob += x_plus[t][m] <= params.charge_rate * y[t]
            prob += x_minus[t][m] <= params.charge_rate * (1 - y[t])

    prob += soc[T] >= params.final_soc_target

    prob += lpSum(
        (mu_df.iloc[t, i] - risk * sigma_df.iloc[t, i]) * params.efficiency * x_plus[t][m]
        - (mu_df.iloc[t, i] + risk * sigma_df.iloc[t, i]) * x_minus[t][m]
        for t in range(T) for i, m in enumerate(markets)
    )

    prob.solve(PULP_CBC_CMD(msg=False, options=[f"randomSeed {SEED}"]))

    status = LpStatus[prob.status]
    profit = value(prob.objective)
    soc_values = [value(soc[t]) for t in range(T+1)]

    schedule, chosen = [], []
    for t in range(T):
        net, mk = 0.0, markets[0]
        for m in markets:
            if value(z[t][m]) > 0.5:
                mk  = m
                net = params.efficiency * (value(x_plus[t][m]) - value(x_minus[t][m]))
        schedule.append(net)
        chosen.append(mk)

    return status, profit, soc_values, schedule, chosen, prob
