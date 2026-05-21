Rebel Foods — Cloud Kitchen P&L Analytics Dashboard
A production-grade interactive analytics dashboard built for Rebel Foods as part of a Data Analyst technical assignment. The dashboard provides comprehensive Profit & Loss analysis across 344 cloud kitchen stores, 5 cities, and 6 months of operational data.

Live Demo

Run locally using the instructions below


Project Overview
This project analyses the Profit & Loss performance of cloud kitchens operated by Rebel Foods across India. It is built using Python, Streamlit, and Plotly and delivers two fully interactive dashboards with real-time filtering, pivot tables, and visual insights.
Key Findings from the Data

344 unique kitchen stores across 5 cities — Ahmedabad, Pune, Bangalore, Mumbai, Hyderabad
52% of store-months are EBITDA negative — highlighting profitability volatility across the network
331 out of 344 stores flip between EBITDA positive and negative across months — indicating high month-to-month variance
Bangalore leads in avg EBITDA% at 17.30% — Mumbai lags at 15.67%
Food wastage (Variance%) is well controlled — averaging only 0.62% of revenue across all zones
East zone outperforms all other zones at 17.17% avg EBITDA%
North zone needs attention — lowest avg EBITDA% at 16.01%


Dashboards
Dashboard 1 — Kitchen Level PNL
A fully filterable table showing per-kitchen Profit and Loss across months.
Filters available:

Store, City, Zone, Month
Revenue Cohort, CM Cohort, EBITDA Category, EBITDA Cohort
EBITDA Range Slider
CM Range Slider
Net Revenue Range Slider

Visualisations:

Monthly KPI cards — Net Revenue, Total EBITDA, Avg GM%, Avg EBITDA%, Active Stores
Net Revenue by Month — bar chart
Revenue Share by City — donut chart
Avg EBITDA% Trend — line chart
EBITDA Positive vs Negative Store Count — bar chart
Store Revenue vs Avg EBITDA% — bubble scatter plot


Dashboard 2 — Variance Level PNL
Variance represents food material wastage as a percentage of revenue.
Filter:

Variance Category bucket filter at top

Sub-Dashboard A — Avg Variance % by Revenue Category:

Pivot table: Revenue Category (rows) x Month (columns)
Values: Average Variance% per category per month
Grand Total row included
Heatmap visualisation below the table

Sub-Dashboard B — Store Count by Revenue Bucket:

Pivot table: Revenue Bucket (rows) x Month (columns)
Values: Count of distinct kitchen stores
Color gradient applied for density
Grand Total row included

Additional Charts:

Store Count by Revenue Bucket — bar chart
Avg Variance% Trend — area chart
Variance% Distribution by Zone — box plot


Tech Stack
ToolVersionPurposePython3.10+Core languageStreamlit1.35.0Dashboard frameworkPlotly5.22.0Interactive visualisationsPandas2.2.0Data manipulation and analysisopenpyxl3.1.2Excel file reading

Project Structure
rebel-foods-dashboard/
│
├── dashboard_final.py        # Main Streamlit application
├── analysis.ipynb            # Jupyter notebook with full EDA
├── Kittchen_PNL_Data.xlsx    # Source data file
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation

Installation and Setup
Step 1 — Clone the repository
bashgit clone https://github.com/rudrakshmala/foods-.git
cd rebel-foods-dashboard
Step 2 — Install dependencies
bashpip install -r requirements.txt
Step 3 — Run the dashboard
bashstreamlit run dashboard_final.py
Step 4 — Open in browser
The app will open automatically at:
http://localhost:8501

Requirements
Create a requirements.txt file with the following:
streamlit==1.35.0
plotly==5.22.0
pandas==2.2.0
openpyxl==3.1.2

Data Description
The dataset contains monthly P&L records for cloud kitchen stores operated by Rebel Foods.
ColumnDescriptionSTOREUnique kitchen store identifierCITYCity where the store operatesZONE MAPPINGGeographic zone — East, West, North, SouthMONTHMonth of the record (Oct 2023 to Mar 2024)NET REVENUEActual revenue after discountsGROSS MARGINNet Revenue minus Ideal Food CostKITCHEN EBITDAOperating profit of the kitchenVARIANCEFood material wastage in rupeesGM%Gross Margin as % of Net RevenueEBITDA%Kitchen EBITDA as % of Net RevenueVARIANCE%Food wastage as % of Net RevenueREVENUE COHORTFixed revenue category labelCM COHORTContribution Margin category labelEBITDA CATEGORYEBITDA positive or negativeEBITDA COHORTEBITDA range bucketSTATUSStore active or inactive status

Performance Optimisation
The dashboard uses @st.cache_data with a TTL of 300 seconds for all data loading and filtering operations.
python@st.cache_data(ttl=300, show_spinner="Loading data...")
def load_data(path):
    # Data is loaded once and cached
    # Refreshes automatically every 5 minutes
    # Supports real-time data source integration
This means:

Data loads once on first run
All filter interactions are instant — no reloading
TTL ensures automatic refresh for live data source connections
Easy to extend to database or API data sources by replacing the Excel reader


Key Insights
1. Revenue is Stable
Monthly revenue ranges consistently from Rs. 121 Cr to Rs. 124 Cr — no major seasonal spikes across 6 months.
2. EBITDA Profitability is Volatile
52% of store-months are EBITDA negative. Average EBITDA% is 16.75% but ranges from -32% to +47% — suggesting significant operational variance across stores.
3. Most Stores Flip Profitability
331 out of 344 stores switch between EBITDA positive and negative across months. Only 13 stores are consistently profitable or loss-making throughout the period.
4. City Performance Varies

Bangalore: 17.30% avg EBITDA% — best performer
Ahmedabad: 17.26% avg EBITDA% — highest total revenue
Mumbai: 15.67% avg EBITDA% — weakest performer despite high revenue potential

5. Food Wastage is Well Controlled
Variance% ranges from only 0.18% to 1.49% of revenue. Zone-wise wastage is nearly identical — East 0.62%, North 0.61%, South 0.62%, West 0.61% — indicating standardised kitchen processes.
6. Gross Margin is Healthy
Average GM% of 58.2% — within the healthy 55-65% range for the food industry.
7. North Zone Needs Attention
North zone has the lowest avg EBITDA% at 16.01% — warrants operational review.

How to Connect to a Live Data Source
Replace the Excel reader in load_data() with a database query:
pythonimport sqlalchemy

@st.cache_data(ttl=300)
def load_data():
    engine = sqlalchemy.create_engine("your_connection_string")
    df = pd.read_sql("SELECT * FROM kitchen_pnl", engine)
    return df
The TTL=300 ensures data refreshes every 5 minutes automatically without any manual intervention.

Author
Rudraksh Mishra

Email: rudraksh733@gmail.com
LinkedIn: linkedin.com/in/rudraksh-mishra-5529a7225
GitHub: github.com/rudrakshmala


Acknowledgements
Built as part of the Data Analyst I technical assignment for Rebel Foods.
Data provided by Rebel Foods hiring team for evaluation purposes.
