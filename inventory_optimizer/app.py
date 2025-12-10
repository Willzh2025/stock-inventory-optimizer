"""
Streamlit application for Demand Forecasting and Inventory Optimization System.

Main entry point for the interactive dashboard.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import project modules
from inventory_optimizer import data
from inventory_optimizer import forecasting
from inventory_optimizer import optimizer_scipy
from inventory_optimizer import optimizer_gurobi
from inventory_optimizer import recommender
from inventory_optimizer import visualization
from inventory_optimizer.config import DEFAULT_FORECAST_WINDOW

# Page configuration
st.set_page_config(
    page_title="Inventory Optimization System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "sales_data" not in st.session_state:
    st.session_state.sales_data = None
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "forecast_df" not in st.session_state:
    st.session_state.forecast_df = None
if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None


def main():
    """Main application function."""
    st.title("Demand Forecasting and Inventory Optimization System")
    st.markdown("""
    An integrated prescriptive analytics tool combining demand forecasting,
    inventory cost modeling, and mathematical optimization to recommend optimal order quantities.
    """)

    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")

        # Data source selection
        data_source = st.radio(
            "Data source",
            options=["Use sample data", "Upload CSV"],
            index=0
        )

        if data_source == "Use sample data":
            try:
                if st.session_state.sales_data is None:
                    st.session_state.sales_data = data.load_sample_data()
                st.success("Sample data loaded")
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
                st.session_state.sales_data = None
        else:
            uploaded_file = st.file_uploader(
                "Upload sales_history.csv",
                type=["csv"],
                help="CSV file with columns: date, sku, quantity"
            )

            if uploaded_file is not None:
                try:
                    st.session_state.sales_data = data.load_uploaded_csv(uploaded_file)
                    st.success("File uploaded successfully")
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
                    st.session_state.sales_data = None
            else:
                st.session_state.sales_data = None

        st.divider()

        # Aggregation frequency
        st.subheader("Forecasting")
        freq_option = st.selectbox(
            "Aggregation frequency",
            options=["Daily", "Weekly", "Monthly"],
            index=1
        )
        freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
        freq = freq_map[freq_option]

        forecast_window = st.number_input(
            "Forecast window",
            min_value=2,
            max_value=52,
            value=DEFAULT_FORECAST_WINDOW,
            help="Number of recent periods to use for forecasting"
        )

        st.divider()

        # Optimization parameters
        st.subheader("Optimization")
        budget_input = st.number_input(
            "Budget (optional)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            help="Maximum total purchasing cost. Set to 0 for no constraint."
        )
        budget = budget_input if budget_input > 0 else None

        capacity_input = st.number_input(
            "Capacity (optional)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Maximum warehouse capacity. Set to 0 for no constraint."
        )
        capacity = capacity_input if capacity_input > 0 else None

        # Engine selection
        engine_option = st.radio(
            "Optimization engine",
            options=["Scipy (Simple)", "Gurobi (Advanced, local only)"],
            index=0
        )

        st.divider()

        # Action buttons
        if st.button("Process Data & Forecast", type="primary"):
            if st.session_state.sales_data is not None:
                try:
                    with st.spinner("Processing data..."):
                        st.session_state.processed_data = data.preprocess_sales(
                            st.session_state.sales_data, freq=freq
                        )

                    if st.session_state.processed_data.empty:
                        st.warning("Processed data is empty. Check your data and frequency selection.")
                    else:
                        with st.spinner("Computing forecasts..."):
                            st.session_state.forecast_df = forecasting.compute_baseline_forecast(
                                st.session_state.processed_data,
                                freq=freq,
                                window=forecast_window
                            )

                        st.success("Data processed and forecasts computed")
                        st.session_state.result_df = None
                        st.session_state.recommendations = None
                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
            else:
                st.error("Please load data first")

        if st.button("Run Optimization"):
            if st.session_state.forecast_df is not None and not st.session_state.forecast_df.empty:
                try:
                    with st.spinner("Optimizing..."):
                        if engine_option == "Scipy (Simple)":
                            st.session_state.result_df = optimizer_scipy.optimize_inventory_scipy(
                                st.session_state.forecast_df,
                                budget=budget,
                                capacity=capacity
                            )
                        else:  # Gurobi
                            try:
                                st.session_state.result_df = optimizer_gurobi.optimize_inventory_gurobi(
                                    st.session_state.forecast_df,
                                    budget=budget,
                                    capacity=capacity
                                )
                            except ImportError:
                                st.warning("Gurobi not available, falling back to Scipy engine.")
                                st.session_state.result_df = optimizer_scipy.optimize_inventory_scipy(
                                    st.session_state.forecast_df,
                                    budget=budget,
                                    capacity=capacity
                                )

                    # Generate recommendations
                    st.session_state.recommendations = recommender.make_recommendations(
                        st.session_state.result_df,
                        budget=budget,
                        capacity=capacity
                    )

                    st.success("Optimization complete")
                except Exception as e:
                    st.error(f"Error during optimization: {str(e)}")
            else:
                st.error("Please process data and compute forecasts first")

    # Main content area
    if st.session_state.sales_data is None:
        st.info("Please load data using the sidebar controls to get started.")
        return

    # Section A: Data Preview
    st.header("Data Preview")
    if st.session_state.processed_data is not None and not st.session_state.processed_data.empty:
        st.subheader("Preprocessed demand data")
        st.dataframe(st.session_state.processed_data.head(20), use_container_width=True)
    else:
        st.warning("No processed data available. Click 'Process Data & Forecast' to preprocess the data.")

    st.divider()

    # Section B: Historical Demand Visualization
    st.header("Historical Demand Visualization")
    if st.session_state.processed_data is not None and not st.session_state.processed_data.empty:
        unique_skus = sorted(st.session_state.processed_data["sku"].unique())
        if unique_skus:
            selected_sku = st.selectbox(
                "Select SKU for detailed view",
                options=unique_skus,
                key="historical_sku"
            )

            fig = visualization.plot_demand_history(
                st.session_state.processed_data,
                selected_sku
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Process data to view historical demand charts.")

    st.divider()

    # Section C: Forecasting
    st.header("Forecasting")
    if st.session_state.forecast_df is not None and not st.session_state.forecast_df.empty:
        st.subheader("Baseline demand forecast per SKU")
        st.dataframe(st.session_state.forecast_df, use_container_width=True)
    else:
        st.warning("No forecast data available. Click 'Process Data & Forecast' to compute forecasts.")

    st.divider()

    # Section D: Optimization
    st.header("Optimization")
    if st.session_state.result_df is not None and not st.session_state.result_df.empty:
        st.subheader("Optimization results")
        st.dataframe(st.session_state.result_df, use_container_width=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Recommended order quantities")
            fig_orders = visualization.plot_order_quantities(st.session_state.result_df)
            st.plotly_chart(fig_orders, use_container_width=True)

        with col2:
            st.subheader("Cost breakdown")
            fig_costs = visualization.plot_cost_breakdown(st.session_state.result_df)
            st.plotly_chart(fig_costs, use_container_width=True)
    else:
        st.info("Click 'Run Optimization' to compute optimal order quantities.")

    st.divider()

    # Section E: Recommendations and Scenario Summary
    st.header("Recommendations and Scenario Summary")
    if st.session_state.recommendations:
        rec = st.session_state.recommendations

        # Key metrics
        if rec["metrics"]:
            metrics = rec["metrics"]
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Cost", f"${metrics.get('total_cost', 0):,.2f}")

            with col2:
                st.metric("Purchasing Cost", f"${metrics.get('total_purchasing_cost', 0):,.2f}")

            with col3:
                budget_util = metrics.get("budget_utilization")
                if budget_util is not None:
                    st.metric(
                        "Budget Utilization",
                        f"{budget_util*100:.1f}%",
                        f"${metrics.get('budget_used', 0):,.2f}"
                    )
                else:
                    st.metric("Budget Used", f"${metrics.get('budget_used', 0):,.2f}")

            with col4:
                capacity_util = metrics.get("capacity_utilization")
                if capacity_util is not None:
                    st.metric(
                        "Capacity Utilization",
                        f"{capacity_util*100:.1f}%",
                        f"{metrics.get('capacity_used', 0):,.1f}"
                    )
                else:
                    st.metric("Capacity Used", f"{metrics.get('capacity_used', 0):,.1f}")

        # Per-SKU breakdown
        if not rec["per_sku"].empty:
            st.subheader("Per-SKU cost breakdown")
            st.dataframe(rec["per_sku"], use_container_width=True)

        # Messages
        if rec["messages"]:
            st.subheader("Key Insights")
            for message in rec["messages"]:
                st.info(message)
    else:
        st.info("Run optimization to see recommendations and insights.")

    st.divider()

    # Section F: Scenario / What-If
    st.header("Scenario Analysis")
    st.markdown("""
    Adjust budget and capacity constraints in the sidebar and re-run optimization
    to see how recommendations change under different scenarios.
    """)


if __name__ == "__main__":
    main()

