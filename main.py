from config import BATTERY, RISK_AVERSION
from simulation import simulate_forecast
from optimization import optimize_battery_DRO
from plotting import plot_battery_soc
from baseline import greedy_daily_arbitrage

# 1. Data prep & simulation
mu_df, sigma_df, sim_df, markets, T = simulate_forecast()

# 2. Optimisation
status, opt_profit, soc_vals, schedule, sel_market, _ = optimize_battery_DRO(mu_df, sigma_df, BATTERY, RISK_AVERSION)
print("Deterministic Multi-Market Optimisation:")
print(" Status:", status)
print(f" MILP Profit: {opt_profit:,.2f} €")
print(f" Final SOC:   {soc_vals[-1]:.2f} kWh")

# 3. Greedy baseline
base_profit, base_soc, base_sched, base_mkt = greedy_daily_arbitrage(sim_df, BATTERY)
print("\nGreedy daily-arbitrage baseline:")
print(f" Profit:    {base_profit:,.2f} €")
print(f" Final SOC: {base_soc[-1]:.2f} kWh")

# 4. Improvement
impr = opt_profit - base_profit
print("\nRelative improvement vs greedy:")
print(f" {impr:,.2f} €  ({impr/abs(base_profit)*100:.1f} %)")

# 5. Plot & save
fig = plot_battery_soc(
    time_index=sim_df.index, soc_values=soc_vals, overall_gain=opt_profit,
    price_df=sim_df, schedule=schedule, selected_market=sel_market,
    baseline_soc=base_soc, baseline_schedule=base_sched, baseline_market=base_mkt
)
fig.write_html("battery_schedule_comparison.html")
print("Plot saved to 'battery_schedule_comparison.html'.")
