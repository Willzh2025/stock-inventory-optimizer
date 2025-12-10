"""
Data loading and preprocessing utilities for sales history data.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def load_sample_data() -> pd.DataFrame:
    """
    Load sample_data/sales_history.csv.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ["date", "sku", "quantity"]

    Raises
    ------
    FileNotFoundError
        If sample data file does not exist
    ValueError
        If required columns are missing
    """
    module_dir = Path(__file__).parent
    sample_file = module_dir / "sample_data" / "sales_history.csv"

    if not sample_file.exists():
        raise FileNotFoundError(f"Sample data file not found: {sample_file}")

    df = pd.read_csv(sample_file)

    # Validate required columns
    required_cols = ["date", "sku", "quantity"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    return df


def load_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """
    Read a user-uploaded CSV from Streamlit.

    Parameters
    ----------
    uploaded_file
        Streamlit uploaded file object

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ["date", "sku", "quantity"]

    Raises
    ------
    ValueError
        If required columns are missing or file is invalid
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")

    # Validate required columns
    required_cols = ["date", "sku", "quantity"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {missing_cols}. "
            f"Found columns: {list(df.columns)}"
        )

    return df


def preprocess_sales(sales_df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """
    Clean and aggregate sales data.

    Parameters
    ----------
    sales_df : pd.DataFrame
        DataFrame with columns ["date", "sku", "quantity"]
    freq : str
        One of {"D", "W", "M"} for daily, weekly, monthly aggregation

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame with columns ["date", "sku", "quantity"]
    """
    if sales_df.empty:
        return pd.DataFrame(columns=["date", "sku", "quantity"])

    df = sales_df.copy()

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove rows with invalid dates
    df = df.dropna(subset=["date"])

    if df.empty:
        return pd.DataFrame(columns=["date", "sku", "quantity"])

    # Ensure quantity is numeric
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df.dropna(subset=["quantity"])

    if df.empty:
        return pd.DataFrame(columns=["date", "sku", "quantity"])

    # Sort by date
    df = df.sort_values("date")

    # Set date as index for resampling
    df = df.set_index("date")

    # Group by SKU and resample by frequency
    result_rows = []
    for sku in df["sku"].unique():
        sku_data = df[df["sku"] == sku].copy()

        # Resample and sum quantities
        resampled = sku_data["quantity"].resample(freq).sum().reset_index()
        resampled["sku"] = sku
        resampled = resampled[["date", "sku", "quantity"]]

        result_rows.append(resampled)

    if not result_rows:
        return pd.DataFrame(columns=["date", "sku", "quantity"])

    # Combine all SKUs
    result_df = pd.concat(result_rows, ignore_index=True)
    result_df = result_df.sort_values(["date", "sku"]).reset_index(drop=True)

    return result_df

