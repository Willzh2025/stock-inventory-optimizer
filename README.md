# Demand Forecasting and Inventory Optimization System

## Overview

This system is an end-to-end prescriptive analytics tool designed for inventory planners and supply chain analysts. It combines demand forecasting, inventory cost modeling, and mathematical optimization to recommend optimal order quantities for multiple SKUs under budget and capacity constraints.

The system addresses the fundamental inventory management challenge: determining how much to order for each product to minimize total costs while respecting financial and physical constraints.

## Problem and Motivation

Inventory management requires balancing multiple competing objectives:

- Minimizing purchasing costs
- Avoiding overstock situations that incur holding costs
- Preventing stockouts that result in lost sales or service penalties
- Operating within budget constraints
- Respecting warehouse capacity limitations

Traditional approaches rely on heuristics or simple rules-of-thumb. This system provides a data-driven, optimization-based approach that explicitly models costs and constraints to generate mathematically sound recommendations.

## Methodology and Workflow

The system implements the following pipeline:

1. **Data Collection and Preparation**: Load historical sales data (date, SKU, quantity) and aggregate at a chosen time frequency (daily, weekly, or monthly).

2. **Demand Forecasting**: For each SKU, estimate expected demand and uncertainty for the next period using a moving average model over recent historical periods.

3. **Cost Modeling**: Assign unit purchase cost, holding cost, stockout penalty, and volume requirements to each SKU. These parameters define the economic trade-offs between overstock and understock scenarios.

4. **Optimization**: Solve a mathematical optimization problem to determine optimal order quantities that minimize expected total cost subject to budget and capacity constraints.

5. **Recommendations**: Convert optimization results into interpretable metrics, per-SKU breakdowns, and actionable insights.

6. **Visualization and UI**: Present results through an interactive Streamlit dashboard with charts, tables, and scenario analysis capabilities.

## Mathematical Model

### Decision Variables

For each SKU i, define:
- Q_i >= 0: order quantity for the upcoming period

### Cost Structure

For each SKU i, define:
- c_i: unit purchase cost
- h_i: holding cost per unit of leftover inventory
- π_i: stockout penalty per unit of unmet demand
- v_i: warehouse space required per unit
- μ_i: expected demand (mean from historical data)

The overstock and understock for SKU i are:
- overstock_i = max(Q_i - μ_i, 0)
- understock_i = max(μ_i - Q_i, 0)

### Objective Function

Minimize total expected cost:

TotalCost = Σ_i [ c_i * Q_i + h_i * overstock_i + π_i * understock_i ]

This captures:
- Purchasing costs: c_i * Q_i
- Holding costs: h_i * overstock_i (cost of excess inventory)
- Shortage costs: π_i * understock_i (penalty for unmet demand)

### Constraints

Budget constraint (if budget B is provided):
Σ_i c_i * Q_i <= B

Capacity constraint (if capacity C is provided):
Σ_i v_i * Q_i <= C

Non-negativity:
Q_i >= 0 for all i

### Optimization Engines

The system provides two optimization engines:

1. **Scipy Engine**: Uses scipy.optimize.minimize with the SLSQP method. This is suitable for cloud deployment and does not require commercial software licenses.

2. **Gurobi Engine**: Uses Gurobi Optimizer for advanced mixed-integer programming capabilities. This requires a Gurobi license and is intended for local use. The system gracefully falls back to Scipy if Gurobi is not available.

## System Architecture

The project follows a modular architecture:

```
inventory_optimizer/
├── app.py                  # Streamlit front-end and orchestration
├── data.py                 # Data loading and preprocessing
├── forecasting.py          # Demand forecasting logic
├── optimizer_scipy.py      # Scipy optimization engine
├── optimizer_gurobi.py     # Gurobi optimization engine (optional)
├── recommender.py          # Recommendations and metrics
├── visualization.py         # Plot generation
├── config.py               # Defaults and configuration helpers
└── sample_data/
    └── sales_history.csv   # Synthetic example data
```

### Module Responsibilities

- **config.py**: Provides default cost parameters and helper functions to enrich forecast data with cost information.

- **data.py**: Handles loading sample data or user-uploaded CSV files, validates required columns, and preprocesses data by aggregating to the selected frequency.

- **forecasting.py**: Implements baseline demand forecasting using a moving window approach. Computes mean and standard deviation of demand for each SKU.

- **optimizer_scipy.py**: Implements the core optimization model using Scipy's SLSQP solver. Handles continuous optimization with budget and capacity constraints.

- **optimizer_gurobi.py**: Implements the same optimization model using Gurobi Optimizer. Provides advanced capabilities and includes proper error handling for missing dependencies.

- **recommender.py**: Converts raw optimization results into interpretable metrics, per-SKU cost breakdowns, and textual insights about the recommendations.

- **visualization.py**: Generates Plotly charts for demand history, order quantities, and cost breakdowns.

- **app.py**: Main Streamlit application that orchestrates all modules and provides the interactive user interface.

## Data Requirements

Input data must be provided as a CSV file with the following columns:

- **date**: Date of the sale (format: YYYY-MM-DD or any pandas-readable date format)
- **sku**: Stock Keeping Unit identifier (string)
- **quantity**: Quantity sold (numeric, non-negative)

The system will automatically:
- Parse dates and handle missing or invalid entries
- Aggregate data to the selected frequency (daily, weekly, or monthly)
- Handle missing values and data quality issues

## Usage

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Install Gurobi for advanced optimization:

```bash
pip install gurobipy
```

Note: Gurobi requires a license. Academic licenses are available free of charge. Visit https://www.gurobi.com/ for more information.

### Running the Application

From the project root directory, run:

```bash
streamlit run inventory_optimizer/app.py
```

The application will open in your default web browser at http://localhost:8501

### Using the Application

1. **Load Data**: 
   - Select "Use sample data" to use the included sample dataset, or
   - Select "Upload CSV" and upload your own sales_history.csv file

2. **Configure Forecasting**:
   - Select aggregation frequency (Daily, Weekly, or Monthly)
   - Set forecast window (number of recent periods to use)

3. **Set Optimization Parameters**:
   - Enter budget constraint (optional, set to 0 for no constraint)
   - Enter capacity constraint (optional, set to 0 for no constraint)
   - Select optimization engine (Scipy or Gurobi)

4. **Process and Optimize**:
   - Click "Process Data & Forecast" to preprocess data and compute forecasts
   - Click "Run Optimization" to solve the optimization problem

5. **Review Results**:
   - View preprocessed data and historical demand charts
   - Examine forecast summaries
   - Analyze optimal order quantities and cost breakdowns
   - Read recommendations and insights

6. **Scenario Analysis**:
   - Adjust budget and capacity constraints in the sidebar
   - Re-run optimization to see how recommendations change

## Optional Gurobi Usage

The Gurobi optimization engine is optional and only used when explicitly selected in the UI. The system is fully functional using only the Scipy engine, which is included in the standard requirements.

Gurobi provides:
- Advanced mixed-integer programming capabilities
- Potentially faster solution times for large problems
- Additional modeling flexibility

If Gurobi is not installed, the system will automatically fall back to the Scipy engine when the Gurobi option is selected.

## License

This project is provided as-is for educational and portfolio purposes.

## Acknowledgments

Built with:
- pandas and numpy for data manipulation
- scipy for optimization
- streamlit for the interactive interface
- plotly for visualizations
- gurobipy for advanced optimization (optional)

