"""
Visualization utilities for demand history, order quantities, and cost breakdowns.
Uses Plotly for interactive charts compatible with Streamlit.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def plot_demand_history(sales_df: pd.DataFrame, sku: str):
    """
    Filter sales_df for given sku and plot quantity vs. date as a line chart.

    Parameters
    ----------
    sales_df : pd.DataFrame
        DataFrame with columns ["date", "sku", "quantity"]
    sku : str
        SKU identifier to plot

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    if sales_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

    # Filter for selected SKU
    sku_data = sales_df[sales_df["sku"] == sku].copy()

    if sku_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for SKU: {sku}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

    # Ensure date is datetime and sort
    if sku_data["date"].dtype != "datetime64[ns]":
        sku_data["date"] = pd.to_datetime(sku_data["date"])
    sku_data = sku_data.sort_values("date")

    # Create line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sku_data["date"],
        y=sku_data["quantity"],
        mode="lines+markers",
        name="Demand",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=f"Historical Demand for SKU: {sku}",
        xaxis_title="Date",
        yaxis_title="Quantity",
        hovermode="x unified",
        template="plotly_white",
        height=400
    )

    return fig


def plot_order_quantities(result_df: pd.DataFrame):
    """
    Plot bar chart of Q_optimal by SKU.

    Parameters
    ----------
    result_df : pd.DataFrame
        DataFrame with columns ["sku", "Q_optimal", ...]

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    if result_df.empty or "Q_optimal" not in result_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No optimization results available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

    df = result_df.copy().sort_values("Q_optimal", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Q_optimal"],
        y=df["sku"],
        orientation="h",
        name="Order Quantity",
        marker=dict(color="#2ca02c", opacity=0.7),
        text=[f"{q:.1f}" for q in df["Q_optimal"]],
        textposition="auto"
    ))

    fig.update_layout(
        title="Optimal Order Quantities by SKU",
        xaxis_title="Order Quantity",
        yaxis_title="SKU",
        template="plotly_white",
        height=max(400, len(df) * 30),
        showlegend=False
    )

    return fig


def plot_cost_breakdown(result_df: pd.DataFrame):
    """
    Plot cost components per SKU as a stacked bar chart.

    Parameters
    ----------
    result_df : pd.DataFrame
        DataFrame with cost components. Should contain columns:
        ["sku", "purchasing_cost", "holding_cost_component", "shortage_cost_component"]
        or these will be computed from available columns.

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    if result_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No cost data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig

    df = result_df.copy()

    # Check if cost columns exist, compute if missing
    required_cols = ["purchasing_cost", "holding_cost_component", "shortage_cost_component"]
    if not all(col in df.columns for col in required_cols):
        # Compute from available columns
        if "Q_optimal" in df.columns and "unit_cost" in df.columns:
            df["purchasing_cost"] = df["unit_cost"] * df["Q_optimal"]
        else:
            df["purchasing_cost"] = 0.0

        if "Q_optimal" in df.columns and "mean_demand" in df.columns:
            df["overstock"] = (df["Q_optimal"] - df["mean_demand"]).clip(lower=0)
            df["understock"] = (df["mean_demand"] - df["Q_optimal"]).clip(lower=0)
        else:
            df["overstock"] = 0.0
            df["understock"] = 0.0

        if "holding_cost" in df.columns:
            df["holding_cost_component"] = df["holding_cost"] * df["overstock"]
        else:
            df["holding_cost_component"] = 0.0

        if "stockout_penalty" in df.columns:
            df["shortage_cost_component"] = df["stockout_penalty"] * df["understock"]
        else:
            df["shortage_cost_component"] = 0.0

    # Sort by SKU for consistent display
    df = df.sort_values("sku")

    # Create stacked bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Purchasing",
        x=df["sku"],
        y=df["purchasing_cost"],
        marker_color="#1f77b4"
    ))

    fig.add_trace(go.Bar(
        name="Holding",
        x=df["sku"],
        y=df["holding_cost_component"],
        marker_color="#ff7f0e"
    ))

    fig.add_trace(go.Bar(
        name="Shortage",
        x=df["sku"],
        y=df["shortage_cost_component"],
        marker_color="#d62728"
    ))

    fig.update_layout(
        title="Cost Breakdown by SKU",
        xaxis_title="SKU",
        yaxis_title="Cost",
        barmode="stack",
        template="plotly_white",
        height=400
    )

    return fig

