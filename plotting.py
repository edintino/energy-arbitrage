import numpy as np
import plotly.graph_objects as go

def plot_battery_soc(time_index, soc_values, overall_gain, price_df,
                     schedule, selected_market,
                     baseline_soc=None, baseline_schedule=None, baseline_market=None):
    def _segment_start_indices(actions, mkts):
        idx, last_a, last_m = [], 0.0, None
        for i,(a,m) in enumerate(zip(actions, mkts)):
            if a == 0:
                last_a, last_m = 0.0, None
            elif last_a==0 or np.sign(a)!=np.sign(last_a) or m!=last_m:
                idx.append(i)
            last_a, last_m = a, m
        return idx

    def _scatter_traces(y_soc, actions, mkts, name, dash, color):
        line = go.Scatter(
            x=time_index, y=y_soc, mode="lines", name=name,
            line=dict(width=2, dash=dash, color=color),
            hovertemplate="SoC: %{y:.1f} kWh<extra></extra>",
        )
        starts = _segment_start_indices(actions, mkts)
        if not starts:
            return [line]
        
        prices = [
            price_df.iat[i, price_df.columns.get_loc(mkts[i])] if actions[i] != 0 else np.nan
            for i in starts
        ]
        hover = [
            f"SoC: {y_soc[i]:.1f} kWh<br>"
            f"Action: {actions[i]:+.1f} kWh<br>"
            f"Market: {mkts[i] if actions[i] != 0 else '–'}<br>"
            f"Price: {prices[j]:.2f} €"
            for j, i in enumerate(starts)
        ]
        markers = go.Scatter(
            x=[time_index[i] for i in starts],
            y=[y_soc[i] for i in starts],
            mode="markers", showlegend=False,
            marker=dict(symbol="circle", size=7, color=color),
            hovertext=hover, hoverinfo="text"
        )
        return [line, markers]

    fig = go.Figure()
    # optimized
    for tr in _scatter_traces(soc_values, schedule, selected_market, "Optimised SoC", "solid", "blue"):
        fig.add_trace(tr)
    # baseline
    if baseline_soc is not None:
        for tr in _scatter_traces(baseline_soc, baseline_schedule, baseline_market, "Greedy baseline SoC", "dash", "red"):
            fig.add_trace(tr)
    fig.update_layout(
        title=(
            "Battery SoC – Optimised vs Greedy"
            f"<sup><br>Total MILP gain: {overall_gain:,.0f} €</sup>"
        ),
        xaxis_title="Time", yaxis_title="State of Charge (kWh)",
        legend=dict(x=0.01, y=0.99), template="plotly_white",
    )
    return fig
