# STAT 5243 Project 2 — Data Explorer

A full-featured, production-grade web application built with Python Shiny (Core mode) that guides users through the complete data science preprocessing workflow — from raw file ingestion to publication-ready exploratory analysis — entirely in the browser with zero coding required. It implements a four-stage reactive pipeline (**Data Loading → Data Cleaning → Feature Engineering → EDA**) connected through a centralized `SharedDataStore` of reactive values, ensuring changes propagate downstream automatically while prerequisite guards prevent skipping stages.

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
- Supports five file formats: CSV, TSV, Excel (.xlsx/.xls), JSON, and Parquet with automatic format detection
- Two built-in sample datasets (Titanic for classification, Ames Housing for regression) for immediate exploration
- Info bar displays filename, format, row/column counts, missing-value percentage, and memory usage
- Interactive filter builder with categorical multi-select and numeric min/max range filters, shown as removable chips
- Column Summary tab with per-column statistics (dtype, missing %, quartiles, mean, std, mode)

### Data Cleaning & Preprocessing
- Ten-step interactive pipeline: standardize missing tokens, format standardization (snake_case, trim, lowercase), drop columns, per-column and bulk imputation, duplicate removal, categorical remapping, type conversion, outlier handling (IQR/Z-score/Percentile), scaling (Standard/MinMax), and encoding (One-Hot/Label)
- Real-time visual feedback via five tabs: Preview, Missing Values bar chart, Distributions histogram, Outliers boxplot, and column Info table
- Multi-step undo (up to 20 snapshots) and an explicit Apply & Save button to commit changes to the pipeline

### Feature Engineering
- Single-column transforms: Log, Log1p, Square Root, Square, Z-Score, Min-Max Scaling, and Binning (adjustable bin count)
- Two-column combinations: Add, Multiply, and Ratio operations for creating interaction features
- Date/time extraction: Year, Month, Day, Day of Week, Hour, Minute, Quarter, Is Weekend, and Day of Year
- Before/after distribution comparison plots, custom feature naming, feature history tracking, undo, and reset to cleaned data

### Exploratory Data Analysis
- Data stage selector lets users compare raw, cleaned, or engineered data side by side
- Six interactive Plotly chart types: Scatter (with optional OLS trendline), Bar (average), Box, Histogram (adjustable bins), Violin, and Pie
- Dynamic numeric range and categorical value filters that update in real time
- Pair plot (scatter matrix) for multi-variable relationships and correlation heatmap with adjustable column limit
- Summary statistics table with count, mean, std, min, quartiles, max, unique, top, and frequency

### User Interface & User Experience
- Navbar layout with resizable sidebars, info-icon popovers providing contextual help, and toast notifications for all operations
- User Guide tab with a complete walkthrough of all four pipeline stages, supported formats table, and usage tips
- Prerequisite guards on each tab prevent users from skipping pipeline stages, displaying clear warning messages
- Well-structured layout with consistent styling across all modules using the Flatly Bootstrap theme (shinyswatch)
- Highly interactive with fast response times, dynamic UI rendering, and smooth end-to-end workflow

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
