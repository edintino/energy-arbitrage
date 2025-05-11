import numpy as np
import plotly.graph_objects as go
from config import BATTERY


def plot_battery_soc(
    time_index,
    soc_opt,
    price_df,
    power_opt,
    market_opt,
    soc_base=None,
    power_base=None,
    market_base=None,
):
    """Plot battery State-of-Charge (left axis) and cumulative gain (right axis)."""

    def cumulative_gain(powers, mkts):
        """kWh → € at each step, accounting for charge efficiency."""
        if powers is None:
            return None
        powers = np.array(powers)
        prices = np.array([price_df.iloc[i][m] for i, m in enumerate(mkts)])
        energy = np.where(powers < 0, powers / BATTERY.efficiency, powers)
        return np.insert(np.cumsum(energy * prices), 0, 0.0)

    fig = go.Figure()

    # --- SoC ------------------------------------------------------------------
    for soc, name, colour in [
        (soc_opt,  "Optimised SoC",        "blue"),
        (soc_base, "Greedy baseline SoC",  "red"),
    ]:
        if soc is not None:
            fig.add_scatter(
                x=time_index,
                y=soc,
                mode="lines",
                name=name,
                line=dict(width=2, dash="dash", color=colour),
                hovertemplate="SoC: %{y:.1f} kWh<extra></extra>",
            )

    # --- Gains (secondary axis) ----------------------------------------------
    fig.update_layout(yaxis2=dict(title="Cumulative Gain (€)", overlaying="y", side="right"))
    for gain, name, colour in [
        (cumulative_gain(power_opt,  market_opt),   "Optimised Gain", "blue"),
        (cumulative_gain(power_base, market_base),  "Greedy Gain",    "red"),
    ]:
        if gain is not None:
            fig.add_scatter(
                x=time_index,
                y=gain,
                yaxis="y2",
                mode="lines",
                name=name,
                line=dict(width=2, color=colour),
            )

    # --- Layout ---------------------------------------------------------------
    fig.update_layout(
        title=f"Battery SoC - Optimised vs Greedy",
            #   f"<sup><br>Total MILP gain: {overall_gain:,.0f} €</sup>",
        xaxis_title="Time",
        yaxis_title="State of Charge (kWh)",
        yaxis_range=[0, BATTERY.battery_capacity],
        legend=dict(x=0.01, y=0.99),
        template="plotly_white",
        hovermode="x unified",
    )
    return fig
