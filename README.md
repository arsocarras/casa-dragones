# Casa Dragones — Analytics & Automation

A collection of analytics dashboards and automation scripts built for Casa Dragones to streamline weekly and monthly data workflows across sales reporting, distribution tracking, and performance analysis.

---

## Projects

### 1. 📊 Nielsen Dashboard (`weekly-sales-dashboard/`)
An interactive Streamlit dashboard for tracking weekly tequila sales performance across U.S. markets. Visualizes This Year vs. Last Year comparisons across five charts — weekly trend lines, % change by week, market-level comparisons, expression mix shifts, and price vs. distribution trends — with dynamic filters by year, expression, and market.

### 2. 🔄 yDrinks Automatization (`ydrinks-automatization/`)
A Python script that automates the weekly merging of individual yDrinks sales activity files into a single, continuously updated historical dataset. Eliminates a time-consuming and error-prone manual process by automatically reading all weekly files and consolidating them into one clean, organized Excel file ready for analysis — reducing a recurring task to under a minute each week.

### 3. 📦 ACV Automatization (`acv-automatization/`)
A Python script that automates the monthly extraction and transformation of the ACV database, which tracks sales performance for all Casa Dragones expressions across U.S. accounts. Automatically produces a clean summary table including This Year vs. Last Year volumes by product, Points of Distribution by expression, state-level ACV share by account, and regional classifications — delivering a fully analysis-ready Excel file in under 30 seconds.

---

## How to Run

### Weekly Sales Dashboard
1. Navigate to the project folder:
   ```bash
   cd nielsen-dashboard
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```
4. Open your browser at `http://localhost:8501`
5. To stop: press `Ctrl + C` in the terminal

### yDrinks Automatization
```bash
cd ydrinks-automatization
pip install -r requirements.txt
python ydrinks_merge.py
```

### ACV Automatization
```bash
cd acv-automatization
pip install -r requirements.txt
python acv_transform.py
```

---

## Data

Each project folder contains or expects its own input data files (`.xlsx`). Data files are sourced internally and should be placed in the corresponding project folder before running. See each project's folder for specific file naming requirements.

> ⚠️ Data files are not committed to this repository. Keep source files local or in a secure shared drive.

---

## Requirements

Each project has its own `requirements.txt`. For the dashboard specifically:

```
streamlit
plotly
openpyxl
pandas
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Deployment

The Weekly Sales Dashboard is deployed via [Streamlit Community Cloud](https://share.streamlit.io). To access the live version, contact the project owner for the link.

---

## Project Structure

```
casa-dragones/
├── nielsen-dashboard/
│   ├── dashboard.py
│   ├── weekly_cleaned.xlsx
│   └── requirements.txt
├── ydrinks-automatization/
│   ├── ydrinks_merge.py
│   └── requirements.txt
├── acv-automatization/
│   ├── acv_transform.py
│   └── requirements.txt
└── README.md
```
