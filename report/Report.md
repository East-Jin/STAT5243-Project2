# Project 2: Data Explorer — Web Application Development and Deployment

**STAT 5243 — Spring 2026**

**Deployed App:** https://zd2372.shinyapps.io/data_explorer/

**GitHub Repository:** https://github.com/East-Jin/STAT5243-Project2

---

## 1. Application Overview

Data Explorer is an interactive web application built with Python Shiny for end-to-end data preprocessing and exploratory data analysis. It features a four-stage pipeline — Data Loading, Data Cleaning, Feature Engineering, and EDA — connected through a shared reactive data store. A dedicated User Guide tab provides step-by-step instructions. The app uses a Flatly Bootstrap theme (shinyswatch) and Plotly for interactive visualizations.

---

## 2. Key Features

### 2.1 Data Loading
- Supports five file formats: CSV, TSV, Excel (.xlsx/.xls), JSON, and Parquet with automatic format detection.
- Two built-in sample datasets (Titanic for classification, Ames Housing for regression) for immediate exploration.
- Info bar displays filename, format, row/column counts, missing-value percentage, and memory usage.
- Interactive filter builder with categorical multi-select and numeric min/max range filters, shown as removable chips.
- Column Summary tab with per-column statistics (dtype, missing %, quartiles, mean, std, mode).

### 2.2 Data Cleaning & Preprocessing
- Ten-step interactive pipeline: standardize missing tokens, format standardization (snake_case, trim, lowercase), drop columns, per-column and bulk imputation, duplicate removal, categorical remapping, type conversion, outlier handling (IQR/Z-score/Percentile), scaling (Standard/MinMax), and encoding (One-Hot/Label).
- Real-time visual feedback via five tabs: Preview, Missing Values bar chart, Distributions histogram, Outliers boxplot, and column Info table.
- Multi-step undo (up to 20 snapshots) and an explicit Apply & Save button to commit changes to the pipeline.

### 2.3 Feature Engineering
- Single-column transforms: Log, Log1p, Square Root, Square, Z-Score, Min-Max Scaling, and Binning (adjustable bin count).
- Two-column combinations: Add, Multiply, and Ratio operations for creating interaction features.
- Date/time extraction: Year, Month, Day, Day of Week, Hour, Minute, Quarter, Is Weekend, and Day of Year.
- Before/after distribution comparison plots, custom feature naming, feature history tracking, undo, and reset to cleaned data.

### 2.4 Exploratory Data Analysis
- Data stage selector lets users compare raw, cleaned, or engineered data side by side.
- Six interactive Plotly chart types: Scatter (with optional OLS trendline), Bar (average), Box, Histogram (adjustable bins), Violin, and Pie.
- Dynamic numeric range and categorical value filters that update in real time.
- Pair plot (scatter matrix) for multi-variable relationships and correlation heatmap with adjustable column limit.
- Summary statistics table with count, mean, std, min, quartiles, max, unique, top, and frequency.

### 2.5 UI/UX & Interactivity
- Navbar layout with resizable sidebars, info-icon popovers with contextual help, and toast notifications for all operations.
- Prerequisite guards on each tab prevent users from skipping pipeline stages, with clear warning messages.
- User Guide tab with a complete walkthrough of all four stages, supported formats table, and usage tips.
- Responsive design, dynamic UI rendering based on data availability, and minimal-lag updates across all modules.

---

## 3. How to Use

1. **Load Data** — Upload a file or select a built-in dataset. Review the data table and column summary. Use filters to narrow rows.
2. **Clean Data** — Apply any combination of the ten preprocessing steps. Preview changes in real time and click *Apply & Save* when satisfied.
3. **Engineer Features** — Create new features using single-column transforms, two-column combinations, or date extraction. Compare before/after distributions and save to the pipeline.
4. **Explore (EDA)** — Select a pipeline stage, apply filters, and choose from six chart types plus pair plots, correlation heatmaps, and summary statistics.

Each tab includes info-icon tooltips for guidance.

---

## 4. Team Member Contributions

| Team Member | UNI | Module | Responsibilities |
|---|---|---|---|
| Zhewei Deng  | zd2372 | Data Loading | File upload, format detection, built-in datasets, filters, column summary; project scaffolding and shared data store architecture; initial data cleaning pipeline; UI enhancements across cleaning and feature engineering tabs; EDA bug fixes and plot expansion; User Guide tab; integration, deployment, and code review |
| Guichen Zheng  | gz2400 | Data Cleaning | 10-step cleaning pipeline, imputation, scaling, encoding, outlier handling |
| Qingyue Wang  | qw2465 | Feature Engineering | Transforms, column combinations, date extraction, before/after plots |
| Xiang Li  | xl3548 | EDA | Interactive plots, pair plots, correlation heatmap, summary statistics |

All team members contributed equally to this project, collaborating on the shared data store architecture, User Guide, UI styling, integration testing, and deployment.

---

## 5. Technology Stack

Python Shiny (Core mode), shinyswatch (Flatly theme), pandas, NumPy, Plotly, Matplotlib, Seaborn, scikit-learn, statsmodels, openpyxl, PyArrow. Deployed on shinyapps.io via rsconnect-python.
