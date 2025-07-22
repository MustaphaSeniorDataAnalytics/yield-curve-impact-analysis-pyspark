# yield-curve-impact-analysis-pyspark
📊 Weekly Yield Curve Analysis Using PySpark : This project addresses a case study focused on analyzing the impact of weekly updates on yield curves using simulation data. The goal is to extract insights into profitability shifts and visualize trends in the discounted Underwriting Ratio (UWR) across time.

🧠 Business Context
SCOR’s pricing tool typically applies quarterly yield curve updates. Due to market volatility, weekly updates were introduced, requiring analytics to:

Track changes in profitability using updated economic assumptions.

Detect yield curve-driven deviations ahead of quarterly updates.

Provide visual tools and KPIs for decision-making.

💻 Tools & Technologies
PySpark: for large-scale data transformation and aggregation.

Python (Pandas, Matplotlib, Seaborn/Plotly): for additional analysis and visualization.

Jupyter Notebooks or Databricks Notebooks: for exploration and development.

📁 Data Used
Weekly re-simulation results (EUR, our share)

Original pricing database export (EUR, our share as at 31.10.2020)

Yield curve input data

🎯 Objective
Measure impact on the discounted Underwriting Ratio (UWR)

Visualize weekly shifts in major yield curves

Connect UWR changes to relevant economic curve movements

Reduce noise in visualization while preserving signal across 52 weeks

Identify trend patterns across the time series

📈 Example Outputs
Yield curve comparison dashboards

Weekly UWR trajectory plots

Filterable sub-portfolio insights

🧠 Key Logic
Curve selection filtering based on business impact

Smoothing / rolling average to reduce visual clutter

Use of deltas and deviation thresholds to highlight significant changes

