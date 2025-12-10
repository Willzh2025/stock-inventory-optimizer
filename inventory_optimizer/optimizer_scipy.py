"""
Scipy-based optimization engine for inventory optimization.
Suitable for cloud deployment as it uses open-source libraries.
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from typing import Optional


def optimize_inventory_scipy(
    params_df: pd.DataFrame,
    budget: float | None,
    capacity: float | None
) -> pd.DataFrame:
    """
    Solve the inventory optimization problem using scipy.optimize.minimize (SLSQP).

    Parameters
    ----------
    params_df : pd.DataFrame
        DataFrame with columns:
        ["sku", "mean_demand", "unit_cost",
         "holding_cost", "stockout_penalty", "volume"]
    budget : float | None
        Maximum total purchasing cost. None indicates no constraint.
    capacity : float | None
        Maximum warehouse capacity. None indicates no constraint.

    Returns
    -------
    pd.DataFrame
        Copy of params_df with added column "Q_optimal"
    """
    if params_df.empty:
        result_df = params_df.copy()
        result_df["Q_optimal"] = 0.0
        return result_df

    n = len(params_df)

    # Extract numpy arrays
    mean_demand = params_df["mean_demand"].values
    c = params_df["unit_cost"].values
    h = params_df["holding_cost"].values
    p = params_df["stockout_penalty"].values
    v = params_df["volume"].values

    # Objective function
    def objective(Q):
        """
        Total cost = purchasing + holding (overstock) + shortage (understock)
        """
        Q = np.maximum(Q, 0)  # Ensure non-negative

        overstock = np.maximum(Q - mean_demand, 0)
        understock = np.maximum(mean_demand - Q, 0)

        purchasing_cost = np.sum(c * Q)
        holding_cost = np.sum(h * overstock)
        shortage_cost = np.sum(p * understock)

        return purchasing_cost + holding_cost + shortage_cost

    # Constraints
    constraints = []

    # Budget constraint: budget - sum(c_i * Q_i) >= 0
    if budget is not None and budget > 0:
        def budget_constraint(Q):
            return budget - np.sum(c * Q)
        constraints.append({"type": "ineq", "fun": budget_constraint})

    # Capacity constraint: capacity - sum(v_i * Q_i) >= 0
    if capacity is not None and capacity > 0:
        def capacity_constraint(Q):
            return capacity - np.sum(v * Q)
        constraints.append({"type": "ineq", "fun": capacity_constraint})

    # Bounds: Q_i >= 0 for all i
    bounds = [(0.0, None)] * n

    # Initial guess: start from mean demand
    Q0 = mean_demand.copy()
    Q0 = np.maximum(Q0, 0.0)

    # If initial guess violates constraints, scale it down
    if budget is not None and budget > 0:
        total_cost = np.sum(c * Q0)
        if total_cost > budget:
            Q0 = Q0 * (budget / total_cost) * 0.95  # Scale down slightly

    if capacity is not None and capacity > 0:
        total_vol = np.sum(v * Q0)
        if total_vol > capacity:
            Q0 = Q0 * (capacity / total_vol) * 0.95  # Scale down slightly

    # Solve optimization problem
    try:
        result = minimize(
            fun=objective,
            x0=Q0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-6}
        )

        if result.success:
            Q_opt = np.maximum(result.x, 0.0)
        else:
            # Optimization failed - use scaled mean demand as fallback
            Q_opt = Q0.copy()
            Q_opt = np.maximum(Q_opt, 0.0)

    except Exception as e:
        # Fallback to initial guess if optimization fails
        Q_opt = Q0.copy()
        Q_opt = np.maximum(Q_opt, 0.0)

    # Create result DataFrame
    result_df = params_df.copy()
    result_df["Q_optimal"] = Q_opt

    return result_df

