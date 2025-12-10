"""
Gurobi-based optimization engine for advanced inventory optimization.
Intended for local use and advanced demonstrations.
"""

import pandas as pd
import numpy as np
from typing import Optional


def optimize_inventory_gurobi(
    params_df: pd.DataFrame,
    budget: float | None,
    capacity: float | None
) -> pd.DataFrame:
    """
    Solve the inventory optimization problem using Gurobi.

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

    Raises
    ------
    ImportError
        If gurobipy is not installed
    """
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        raise ImportError(
            "Gurobi is not available. Please install gurobipy for the advanced engine."
        )

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

    # Create Gurobi model
    m = gp.Model("inventory_optimization")
    m.setParam("OutputFlag", 0)  # Suppress Gurobi output

    # Decision variables: Q[i] >= 0
    Q = m.addVars(n, lb=0.0, name="Q")

    # Auxiliary variables for overstock and understock
    overstock = m.addVars(n, lb=0.0, name="overstock")
    understock = m.addVars(n, lb=0.0, name="understock")

    # Constraints for overstock and understock
    for i in range(n):
        # overstock[i] >= Q[i] - mean_demand[i]
        m.addConstr(overstock[i] >= Q[i] - mean_demand[i], name=f"overstock_{i}")
        # understock[i] >= mean_demand[i] - Q[i]
        m.addConstr(understock[i] >= mean_demand[i] - Q[i], name=f"understock_{i}")

    # Budget constraint
    if budget is not None and budget > 0:
        m.addConstr(
            gp.quicksum(c[i] * Q[i] for i in range(n)) <= budget,
            name="budget"
        )

    # Capacity constraint
    if capacity is not None and capacity > 0:
        m.addConstr(
            gp.quicksum(v[i] * Q[i] for i in range(n)) <= capacity,
            name="capacity"
        )

    # Objective: minimize total cost
    purchasing = gp.quicksum(c[i] * Q[i] for i in range(n))
    holding = gp.quicksum(h[i] * overstock[i] for i in range(n))
    shortage = gp.quicksum(p[i] * understock[i] for i in range(n))

    m.setObjective(purchasing + holding + shortage, GRB.MINIMIZE)

    # Optimize
    try:
        m.optimize()

        if m.status == GRB.OPTIMAL:
            Q_opt = np.array([Q[i].X for i in range(n)])
            Q_opt = np.maximum(Q_opt, 0.0)  # Ensure non-negative
        else:
            # Fallback to mean demand if optimization fails
            Q_opt = mean_demand.copy()
            Q_opt = np.maximum(Q_opt, 0.0)

    except Exception as e:
        # Fallback to mean demand if optimization fails
        Q_opt = mean_demand.copy()
        Q_opt = np.maximum(Q_opt, 0.0)

    # Create result DataFrame
    result_df = params_df.copy()
    result_df["Q_optimal"] = Q_opt

    return result_df

