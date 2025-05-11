import numpy as np
import pandas as pd
from config import BATTERY

def greedy_daily_arbitrage(sim_df: pd.DataFrame, params=BATTERY):
    cap = params.battery_capacity
    p_max = params.charge_rate
    soc0 = params.initial_soc
    eta = params.efficiency
    soc_min = params.battery_capacity_buffer * params.battery_capacity
    soc_max = (1 - params.battery_capacity_buffer) * params.battery_capacity

    T = len(sim_df)
    days = sim_df.index.normalize()

    soc = np.empty(T+1); soc[0] = soc0
    sched = np.zeros(T)
    market = [''] * T

    n_slots = int(np.ceil(cap / p_max))

    for day, grp in sim_df.groupby(days):
        idx = grp.index
        loc = sim_df.index.get_indexer(idx)
        to_charge = grp.min(axis=1).nsmallest(n_slots).index
        to_discharge = grp.max(axis=1).nlargest(n_slots).index

        for i, ts in enumerate(idx):
            t = loc[i]
            if ts in to_charge and soc[t] < soc_max:
                e = min(p_max, (soc_max - soc[t]) / eta)
                sched[t] = -e
                soc[t+1] = soc[t] + e * eta
                market[t] = grp.columns[grp.iloc[i].argmin()]
            elif ts in to_discharge and soc[t] > soc_min:
                e = min(p_max, soc[t] - soc_min)
                sched[t] = e * eta
                soc[t+1] = soc[t] - e
                market[t] = grp.columns[grp.iloc[i].argmax()]
            else:
                soc[t+1] = soc[t]
                market[t] = grp.columns[grp.iloc[i].argmax()]

    # restore initial SOC
    diff = soc[-1] - soc0
    if abs(diff) > 1e-6:
        nz = np.nonzero(sched)[0]
        if nz.size:
            sched[nz[-1]] -= diff
            soc[-1] = soc0

    profit = float(sum(sched[i] * sim_df.iloc[i][market[i]] for i in range(T)))
    return profit, soc[:-1], sched, market
