"""
Demand forecasting functions for predicting future SKU demand.
"""

import pandas as pd
import numpy as np
from .config import DEFAULT_FORECAST_WINDOW, apply_default_costs


def compute_baseline_forecast(
    sales_df: pd.DataFrame,
    freq: str = "W",
    window: int | None = None
) -> pd.DataFrame:
    """
    Compute baseline demand forecasts per SKU using a moving window.

    Parameters
    ----------
    sales_df : pd.DataFrame
        Pre-aggregated DataFrame with columns ["date", "sku", "quantity"]
        at frequency freq
    freq : str, default "W"
        Frequency string (for reference, not used in calculation)
    window : int | None, default None
        Number of recent periods to use. If None, uses DEFAULT_FORECAST_WINDOW

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        ["sku", "mean_demand", "std_demand", "unit_cost",
         "holding_cost", "stockout_penalty", "volume"]
    """
    if sales_df.empty:
        forecast_df = pd.DataFrame(columns=[
            "sku", "mean_demand", "std_demand", "unit_cost",
            "holding_cost", "stockout_penalty", "volume"
        ])
        return apply_default_costs(forecast_df)

    if window is None:
        window = DEFAULT_FORECAST_WINDOW

    # Ensure date is datetime
    if sales_df["date"].dtype != "datetime64[ns]":
        sales_df = sales_df.copy()
        sales_df["date"] = pd.to_datetime(sales_df["date"])

    # Group by SKU and compute forecasts
    forecast_rows = []

    for sku in sales_df["sku"].unique():
        sku_data = sales_df[sales_df["sku"] == sku].copy()
        sku_data = sku_data.sort_values("date")

        # Take the last window periods (or all if fewer available)
        recent_data = sku_data.tail(window)

        if len(recent_data) > 0:
            quantities = recent_data["quantity"].values
            mean_demand = float(np.mean(quantities))
            std_demand = float(np.std(quantities)) if len(quantities) >= 2 else 0.0

            # Ensure non-negative
            mean_demand = max(0.0, mean_demand)
            std_demand = max(0.0, std_demand)
        else:
            mean_demand = 0.0
            std_demand = 0.0

        forecast_rows.append({
            "sku": sku,
            "mean_demand": mean_demand,
            "std_demand": std_demand
        })

    forecast_df = pd.DataFrame(forecast_rows)

    # Apply default costs
    forecast_df = apply_default_costs(forecast_df)

    return forecast_df

