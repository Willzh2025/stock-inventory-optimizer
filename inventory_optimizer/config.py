"""
Configuration constants and helper functions for the inventory optimization system.
"""

import pandas as pd

# Default cost parameters
DEFAULT_UNIT_COST = 10.0
DEFAULT_HOLDING_COST = 1.0
DEFAULT_STOCKOUT_PENALTY = 5.0
DEFAULT_VOLUME = 1.0

# Forecasting defaults
DEFAULT_FORECAST_WINDOW = 8


def apply_default_costs(forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure that forecast_df contains the following columns:
    - unit_cost
    - holding_cost
    - stockout_penalty
    - volume

    For any missing column, add it and fill with default constants.
    Do not overwrite existing non-null values if the columns exist.

    Parameters
    ----------
    forecast_df : pd.DataFrame
        DataFrame that should contain cost columns

    Returns
    -------
    pd.DataFrame
        DataFrame with all required cost columns populated
    """
    df = forecast_df.copy()

    # Add missing columns with default values
    if 'unit_cost' not in df.columns:
        df['unit_cost'] = DEFAULT_UNIT_COST
    elif df['unit_cost'].isna().any():
        df['unit_cost'] = df['unit_cost'].fillna(DEFAULT_UNIT_COST)

    if 'holding_cost' not in df.columns:
        df['holding_cost'] = DEFAULT_HOLDING_COST
    elif df['holding_cost'].isna().any():
        df['holding_cost'] = df['holding_cost'].fillna(DEFAULT_HOLDING_COST)

    if 'stockout_penalty' not in df.columns:
        df['stockout_penalty'] = DEFAULT_STOCKOUT_PENALTY
    elif df['stockout_penalty'].isna().any():
        df['stockout_penalty'] = df['stockout_penalty'].fillna(DEFAULT_STOCKOUT_PENALTY)

    if 'volume' not in df.columns:
        df['volume'] = DEFAULT_VOLUME
    elif df['volume'].isna().any():
        df['volume'] = df['volume'].fillna(DEFAULT_VOLUME)

    return df

