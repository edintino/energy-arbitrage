from config import BATTERY, RISK_AVERSION
from simulation import simulate_forecast
from optimization import optimize_battery_DRO
from plotting import plot_battery_soc
from baseline import greedy_daily_arbitrage

# 1. Data prep & simulation
mu_df, sigma_df, price_df, markets, T = simulate_forecast()

# 2. Optimisation
status, _, soc_opt, power_opt, market_opt, _ = optimize_battery_DRO(mu_df, sigma_df, BATTERY, RISK_AVERSION)

# 3. Greedy baseline
_, soc_base, power_base, market_base = greedy_daily_arbitrage(price_df, BATTERY)

# 4. Plot & save
fig = plot_battery_soc(
    time_index=price_df.index, soc_opt=soc_opt, price_df=price_df,
    power_opt=power_opt, market_opt=market_opt, soc_base=soc_base,
    power_base=power_base, market_base=market_base
)
fig.write_html("battery_schedule_comparison.html")
print("Plot saved to 'battery_schedule_comparison.html'.")
