# Demand Forecasting & Inventory Optimization System

> A prescriptive analytics application that generates optimal order quantity recommendations under demand uncertainty, budget limits, and warehouse capacity constraints. Designed for supply chain analysts and inventory planners.

## The Problem

Inventory planning requires choosing order quantities before actual demand is known. Ordering too much leads to excess inventory, tied-up capital, and high holding costs. Ordering too little results in stockouts, lost sales, and customer dissatisfaction. Because each SKU may have different demand patterns, costs, and operational constraints, simple heuristics often fail in real-world settings.

As organizations manage larger SKU portfolios and operate under multiple constraints such as purchasing budget and warehouse capacity, spreadsheet-based or rule-based approaches become insufficient. A data-driven, optimization-based solution is needed to systematically connect historical demand, economic trade-offs, and business constraints into a single decision model.

## The Solution

This system provides a complete prescriptive analytics workflow that transforms raw sales data into optimal order recommendations using forecasting, cost modeling, and constrained optimization.

For each SKU i, the system determines an order quantity Q_i. With the following parameters:

- c_i: unit purchase cost  
- h_i: holding cost per unit of excess inventory  
- p_i: shortage penalty per unit of unmet demand  
- v_i: warehouse space per unit  
- mu_i: forecasted mean demand  

The system calculates:

overstock_i = max(Q_i − mu_i, 0)  
understock_i = max(mu_i − Q_i, 0)

Total cost across all SKUs is:

TotalCost = sum over i of [ c_i * Q_i + h_i * overstock_i + p_i * understock_i ]

Optional constraints:

Budget: sum over i of (c_i * Q_i) <= B  
Capacity: sum over i of (v_i * Q_i) <= C

The optimization engine finds the set of Q_i values that minimizes total expected cost while satisfying all constraints. The system also produces cost breakdowns, charts, and business-friendly insights describing the drivers behind the optimal recommendations.

## Live Demo

Replace with your deployment link:

https://your-streamlit-app-url.streamlit.app

![Main Screenshot](images/screenshot_main.png)

## How It Works

### Step 1: Data Input and Preprocessing
Users may:
- Upload a CSV file containing columns: date, sku, quantity  
- Or use the provided sample dataset at inventory_optimizer/sample_data/sales_history.csv

The system:
- Parses dates  
- Aggregates the data (daily, weekly, or monthly)  
- Handles missing values  
- Produces a clean SKU-by-period demand table  

### Step 2: Demand Forecasting and Cost Assignment
For each SKU, the system examines the most recent N periods (default: 8) and computes:
- mean demand (mu_i)  
- standard deviation (uncertainty measure)  

Cost parameters assigned per SKU:
- unit_cost (c_i)  
- holding_cost (h_i)  
- stockout_penalty (p_i)  
- volume requirement (v_i)  

Defaults are applied automatically if the user does not specify values.

### Step 3: Optimization
The user selects:
- Budget constraint (optional)  
- Capacity constraint (optional)  
- Optimization engine: SciPy or Gurobi  

The system constructs the optimization problem using:
- forecasted demand  
- cost structure  
- selected constraints  

SciPy solves via SLSQP (nonlinear optimization).  
Gurobi solves a linearized formulation (when available).

The solver outputs optimal order quantities Q_i.

### Step 4: Recommendations and Insights
The system generates:
- Cost breakdown per SKU (purchasing, holding, shortage)  
- Overall cost metrics  
- Budget and capacity utilization  
- Visualizations: demand history, order quantities, cost composition  
- A set of short insights summarizing key drivers and patterns  

### The Analytics Behind It

Data used:
- Historical sales  
- User-provided or default cost values  
- Budget and capacity constraints  

Models used:
- Moving-average forecast  
- Constrained cost minimization model  

How recommendations are generated:
- The solver finds Q_i values that minimize total cost  
- The system interprets results into tables, charts, and business insights

## Example Output

### Forecast Summary Table
Columns include:
- sku  
- mean_demand  
- std_demand  
- unit_cost  
- holding_cost  
- stockout_penalty  
- volume  

Example:

![Forecast Summary](images/forecast_summary.png)

### Optimal Order Quantities
Includes:
- expected demand mu_i  
- optimal order quantity Q_i  
- ratio Q_i / mu_i  

![Optimal Orders](images/optimal_orders.png)

### Cost Breakdown
Shows:
- purchasing cost  
- holding cost  
- shortage cost  
- total cost  

![Cost Breakdown](images/cost_breakdown.png)

### Key Metrics
- total purchasing cost  
- total holding cost  
- total shortage cost  
- total expected cost  
- budget usage  
- capacity usage  

### Insights
Examples:
- A specific SKU may drive a large share of total cost  
- Budget or capacity constraints may be binding  
- Some SKUs may optimally be ordered below forecast due to high holding cost  

## Technology Stack

- Streamlit (UI and dashboards)  
- SciPy (SLSQP optimization)  
- Gurobi (optional advanced solver)  
- pandas and numpy (data handling and preprocessing)  
- Plotly (interactive charts)  
- CSV data input  

## About This Project

Developed for ISOM 839 – Prescriptive Analytics at Suffolk University.

Demonstrates:
- End-to-end prescriptive analytics workflow  
- Mathematical optimization modeling  
- Forecasting and cost modeling  
- Interactive decision-support system development  
- Clear communication of analytical insights  

Author: Your Name  
LinkedIn: Your URL  
Email: your.email@example.com  

## Future Possibilities

- Multi-period planning with lead times  
- Advanced forecasting models (ARIMA, exponential smoothing, ML models)  
- Service-level constraints  
- Quantity discounts and supplier constraints  
- SKU substitution or complementarity modeling  
- ERP/WMS integration  
- Enhanced scenario analysis tools  

## Demo Video

Place your video in:
videos/demo.mp4

Link it here:
[Watch the walkthrough](videos/demo.mp4)
