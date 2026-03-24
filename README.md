# STAT 5243 Project 2 — Data Explorer

A Python Shiny web application for interactive data loading, cleaning, feature engineering, and exploratory data analysis.

**Live App:** https://zd2372.shinyapps.io/data_explorer/

## Quick Start

### 1. Install uv (Python package manager)

We use [uv](https://docs.astral.sh/uv/) to manage the Python environment. It automatically downloads Python 3.11 — no global install needed.

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and set up the environment

```bash
git clone https://github.com/East-Jin/STAT5243-Project2.git
cd STAT5243-Project2

# Create a Python 3.11 virtual environment
uv venv --python 3.11

# Activate it
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Run the app

```bash
shiny run app.py
```

The app will be available at `http://localhost:8000`.

**Dev Mode** — pre-fills all pipeline stages with Titanic sample data so you can jump to any tab:

```bash
DEV_MODE=true shiny run app.py
```

## Features

### Data Loading
- Upload files in five formats: CSV, TSV, Excel (.xlsx/.xls), JSON, Parquet
- Two built-in sample datasets: Titanic (classification) and Ames Housing (regression)
- Dataset info bar (filename, format, rows, columns, missing %, memory)
- Interactive filter builder with categorical multi-select and numeric range filters
- Column summary with per-column statistics

### Data Cleaning & Preprocessing
- 10-step interactive pipeline: standardize missing tokens, format standardization, drop columns, per-column and bulk imputation, duplicate removal, categorical remapping, type conversion, outlier handling (IQR/Z-score/Percentile), scaling (Standard/MinMax), encoding (One-Hot/Label)
- Real-time visual feedback: Preview, Missing Values chart, Distributions, Outliers, Info tabs
- Multi-step undo (up to 20 snapshots)

### Feature Engineering
- Single-column transforms: Log, Log1p, Square Root, Square, Z-Score, Min-Max, Binning
- Two-column combinations: Add, Multiply, Ratio
- Date/time extraction: Year, Month, Day, Day of Week, Hour, Minute, Quarter, Is Weekend, Day of Year
- Before/after distribution plots, feature history tracking, undo and reset

### Exploratory Data Analysis
- Compare raw, cleaned, or engineered data side by side
- Six interactive Plotly chart types: Scatter (with OLS trendline), Bar, Box, Histogram, Violin, Pie
- Dynamic numeric and categorical filters
- Pair plot (scatter matrix) and correlation heatmap
- Summary statistics table

### User Guide
- Built-in walkthrough of all four pipeline stages with tips and supported format reference

## Project Structure

```
app.py                      # Entry point — navbar, store init, module wiring
modules/
    user_guide.py           # In-app documentation (UI only)
    data_loading.py         # Upload, format detection, filters, column summary
    data_cleaning.py        # 10-step cleaning pipeline
    feature_engineering.py  # Transforms, combinations, date extraction
    eda.py                  # Interactive plots, pair plot, heatmap, statistics
shared/
    data_store.py           # SharedDataStore — reactive pipeline state
    sample_datasets.py      # Titanic & Ames Housing loaders
data/
    titanic.csv             # Built-in sample dataset
    ames_housing.csv        # Built-in sample dataset
docs/
    ARCHITECTURE.md         # Architecture details and data flow
report/
    Report.md               # Project report
    Report.pdf              # Project report (PDF)
```

## Team

| Member | UNI | Module | Responsibilities |
|--------|-----|--------|------------------|
| Zhewei Deng | zd2372 | Data Loading | File upload, filters, column summary; project scaffolding and shared data store; initial cleaning pipeline; UI enhancements across modules; User Guide; integration and deployment |
| Guichen Zheng | gz2400 | Data Cleaning | 10-step cleaning pipeline, imputation, scaling, encoding, outlier handling |
| Qingyue Wang | qw2465 | Feature Engineering | Transforms, column combinations, date extraction, before/after plots |
| Xiang Li | xl3548 | EDA | Interactive plots, pair plots, correlation heatmap, summary statistics |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture, data flow diagrams, and shared data store contract.

## Deployment

The app is deployed on shinyapps.io. To redeploy:

```bash
rsconnect add --account <ACCOUNT> --name shinyapps --token <TOKEN> --secret <SECRET>
rsconnect deploy shiny . --name shinyapps --title "Data Explorer"
```

## Tech Stack

Python Shiny (Core mode), shinyswatch (Flatly theme), pandas, NumPy, Plotly, Matplotlib, Seaborn, scikit-learn, statsmodels, openpyxl, PyArrow.
