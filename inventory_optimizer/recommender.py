"""
Recommendation and summary generation for inventory optimization results.
"""

import pandas as pd
import numpy as np
from typing import Optional


def make_recommendations(
    result_df: pd.DataFrame,
    budget: float | None,
    capacity: float | None
) -> dict:
    """
    Compute cost breakdown and high-level recommendations.

    Parameters
    ----------
    result_df : pd.DataFrame
        DataFrame with columns:
        ["sku", "mean_demand", "Q_optimal", "unit_cost",
         "holding_cost", "stockout_penalty", "volume"]
    budget : float | None
        Budget constraint used (if any)
    capacity : float | None
        Capacity constraint used (if any)

    Returns
    -------
    dict
        Dictionary with keys:
        - "metrics": dict of aggregate metrics
        - "per_sku": DataFrame with per-SKU cost breakdown
        - "messages": list of short textual insights
    """
    if result_df.empty:
        return {
            "metrics": {},
            "per_sku": pd.DataFrame(),
            "messages": ["No data available for recommendations."]
        }

    df = result_df.copy()

    # Compute overstock and understock per SKU
    df["overstock"] = np.maximum(df["Q_optimal"] - df["mean_demand"], 0)
    df["understock"] = np.maximum(df["mean_demand"] - df["Q_optimal"], 0)

    # Compute per-SKU costs
    df["purchasing_cost"] = df["unit_cost"] * df["Q_optimal"]
    df["holding_cost_component"] = df["holding_cost"] * df["overstock"]
    df["shortage_cost_component"] = df["stockout_penalty"] * df["understock"]
    df["total_cost"] = (
        df["purchasing_cost"] +
        df["holding_cost_component"] +
        df["shortage_cost_component"]
    )

    # Aggregate totals
    total_purchasing_cost = float(df["purchasing_cost"].sum())
    total_holding_cost = float(df["holding_cost_component"].sum())
    total_shortage_cost = float(df["shortage_cost_component"].sum())
    total_cost = float(df["total_cost"].sum())

    # Budget and capacity usage
    budget_used = total_purchasing_cost
    budget_utilization = None
    if budget is not None and budget > 0:
        budget_utilization = budget_used / budget

    capacity_used = float((df["volume"] * df["Q_optimal"]).sum())
    capacity_utilization = None
    if capacity is not None and capacity > 0:
        capacity_utilization = capacity_used / capacity

    # Build metrics dictionary
    metrics = {
        "total_purchasing_cost": total_purchasing_cost,
        "total_holding_cost": total_holding_cost,
        "total_shortage_cost": total_shortage_cost,
        "total_cost": total_cost,
        "budget_used": budget_used,
        "budget_utilization": budget_utilization,
        "capacity_used": capacity_used,
        "capacity_utilization": capacity_utilization,
        "n_skus": len(df)
    }

    # Per-SKU breakdown
    per_sku = df[[
        "sku", "mean_demand", "Q_optimal",
        "purchasing_cost", "holding_cost_component",
        "shortage_cost_component", "total_cost"
    ]].copy()

    # Identify notable SKUs
    top_cost_skus = df.nlargest(3, "total_cost")["sku"].tolist()
    high_order_skus = df[df["Q_optimal"] > df["mean_demand"] * 1.2]["sku"].tolist()
    low_order_skus = df[df["Q_optimal"] < df["mean_demand"] * 0.8]["sku"].tolist()

    # Generate messages
    messages = []

    # Overall cost breakdown
    if total_cost > 0:
        pct_purchasing = (total_purchasing_cost / total_cost) * 100
        pct_holding = (total_holding_cost / total_cost) * 100
        pct_shortage = (total_shortage_cost / total_cost) * 100
        messages.append(
            f"Total cost breakdown: {pct_purchasing:.1f}% purchasing, "
            f"{pct_holding:.1f}% holding, {pct_shortage:.1f}% shortage."
        )

    # Budget utilization
    if budget_utilization is not None:
        if budget_utilization > 0.95:
            messages.append(
                f"Budget utilization is {budget_utilization*100:.1f}%. "
                "Consider increasing budget to allow for more optimal ordering."
            )
        elif budget_utilization < 0.5:
            messages.append(
                f"Budget utilization is {budget_utilization*100:.1f}%. "
                "Current budget constraint is not binding."
            )

    # Capacity utilization
    if capacity_utilization is not None:
        if capacity_utilization > 0.95:
            messages.append(
                f"Capacity utilization is {capacity_utilization*100:.1f}%. "
                "Warehouse capacity is nearly fully utilized."
            )
        elif capacity_utilization < 0.5:
            messages.append(
                f"Capacity utilization is {capacity_utilization*100:.1f}%. "
                "Current capacity constraint is not binding."
            )

    # Top cost contributors
    if top_cost_skus:
        messages.append(
            f"Top cost-contributing SKUs: {', '.join(top_cost_skus)}. "
            "These drive the majority of total costs."
        )

    # High order quantities
    if high_order_skus:
        messages.append(
            f"SKUs with order quantities significantly above mean demand: "
            f"{', '.join(high_order_skus)}. "
            "These may have high stockout penalties or high demand variability."
        )

    # Low order quantities
    if low_order_skus:
        messages.append(
            f"SKUs with order quantities below mean demand: "
            f"{', '.join(low_order_skus)}. "
            "These may be constrained by budget or capacity, or have low stockout penalties."
        )

    # Cost dominance
    if total_holding_cost > total_shortage_cost * 1.5:
        messages.append(
            "Holding costs dominate shortage costs. "
            "Consider reducing order quantities to minimize overstock risk."
        )
    elif total_shortage_cost > total_holding_cost * 1.5:
        messages.append(
            "Shortage costs dominate holding costs. "
            "Consider increasing order quantities to reduce stockout risk."
        )

    return {
        "metrics": metrics,
        "per_sku": per_sku,
        "messages": messages
    }

