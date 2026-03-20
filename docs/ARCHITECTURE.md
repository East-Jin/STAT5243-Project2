# Architecture — Data Explorer (STAT5243 Project 2)

## Project Overview

This is a Python Shiny web application for interactive data preprocessing and exploratory data analysis. It covers the 6 graded components from the project rubric:

| # | Component | Points | Status |
|---|-----------|--------|--------|
| 1 | Loading Datasets | 8 | Skeleton + working CSV/built-in loader |
| 2 | Data Cleaning & Preprocessing | 8 | Skeleton + working drop-NaN example |
| 3 | Feature Engineering | 8 | Skeleton + working log-transform example |
| 4 | Exploratory Data Analysis | 8 | Skeleton + working plotly histogram |
| 5 | UI / UX | 8 | Basic navbar layout (to be polished together) |
| 6 | Interactivity & Responsiveness | 8 | Reactive framework in place |

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                     app.py                               │
│  ┌──────────────────────────────────────────────────┐    │
│  │           ui.page_navbar (top tabs)               │    │
│  │  ┌──────────┬──────────┬──────────┬──────────┐   │    │
│  │  │  Data    │  Data    │ Feature  │   EDA    │   │    │
│  │  │ Loading  │ Cleaning │   Eng    │          │   │    │
│  │  └────┬─────┴────┬─────┴────┬─────┴────┬─────┘   │    │
│  └───────┼──────────┼──────────┼──────────┼──────┘    │
│          │          │          │          │            │
│  ┌───────▼──────────▼──────────▼──────────▼──────┐    │
│  │          SharedDataStore (reactive)            │    │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │    │
│  │  │ raw_data │ │ cleaned  │ │  engineered   │  │    │
│  │  │          │ │  _data   │ │    _data      │  │    │
│  │  └──────────┘ └──────────┘ └───────────────┘  │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

The modules form a pipeline. Each module reads from the previous stage and writes to the next:

```
Data Loading ──writes──► raw_data
                              │
                         reads│
                              ▼
Data Cleaning ──writes──► cleaned_data
                              │
                         reads│
                              ▼
Feature Eng ──writes──► engineered_data
                              │
                         reads│
                              ▼
EDA (reads raw, cleaned, or engineered — user selects)
```

**Runtime enforcement**: Each module (except Data Loading) contains a prerequisite guard at the top of its server function. If the required upstream data is `None`, the module displays a warning message instead of its controls. These guards are marked with `# === PREREQUISITE GUARD (DO NOT MODIFY) ===` and should not be edited.

## Shared Data Store Contract

The `SharedDataStore` class (in `shared/data_store.py`) holds reactive values for each pipeline stage:

| Reactive Value | Type | Set By | Read By |
|----------------|------|--------|---------|
| `raw_data` | `pd.DataFrame \| None` | Data Loading | Data Cleaning, EDA |
| `cleaned_data` | `pd.DataFrame \| None` | Data Cleaning | Feature Engineering, EDA |
| `engineered_data` | `pd.DataFrame \| None` | Feature Engineering | EDA |
| `data_info` | `dict` | Data Loading | All (for display) |

**Helper methods:**
- `get_latest_data()` — returns the most-processed DataFrame available
- `get_latest_stage_name()` — returns `"engineered"`, `"cleaned"`, `"raw"`, or `"none"`
- `dev_mode_init()` — pre-fills all stages with iris data for independent testing

## Module Responsibility Table

| Module File | Team Member | Reads | Writes | Skeleton Provides |
|-------------|-------------|-------|--------|-------------------|
| `modules/data_loading.py` | Member 1 | — | `raw_data`, `data_info` | CSV upload, built-in dataset selector, data preview |
| `modules/data_cleaning.py` | Member 2 | `raw_data` | `cleaned_data` | Missing value summary, drop-NaN button, working copy pattern |
| `modules/feature_engineering.py` | Member 3 | `cleaned_data` | `engineered_data` | Column selector, log/sqrt transform, preview pattern |
| `modules/eda.py` | Member 4 | all stages | — | Data stage selector, plotly histogram, summary statistics |

## File Structure

```
app.py                              # Main entry — navbar, tabs, wires modules + store
modules/
    __init__.py                     # Re-exports all module UIs and servers
    data_loading.py                 # Member 1: upload + built-in datasets
    data_cleaning.py                # Member 2: missing values, duplicates, scaling, encoding
    feature_engineering.py          # Member 3: create/modify features
    eda.py                          # Member 4: interactive visualizations + stats
shared/
    __init__.py                     # Re-exports SharedDataStore and sample dataset helpers
    data_store.py                   # SharedDataStore class with reactive values
    sample_datasets.py              # Built-in iris + wine datasets via sklearn
docs/
    ARCHITECTURE.md                 # This file
requirements.txt                    # Python dependencies
README.md                          # Quick-start setup guide
```

## Module File Structure

Every module file follows the same pattern:

```python
@module.ui
def my_module_ui():
    return ui.layout_sidebar(
        ui.sidebar(...),          # Controls
        # Main panel outputs
        # === TODO: ADD YOUR FEATURES BELOW ===
    )

@module.server
def my_module_server(input, output, session, shared_store):
    # === PREREQUISITE GUARD (DO NOT MODIFY) ===
    @render.ui
    def guard_message():
        if shared_store.some_data() is None:
            return ui.div(...)    # Warning message
        return ui.TagList()
    # === END GUARD ===

    # ... working example code ...

    # === TODO: ADD YOUR FEATURES BELOW ===
```

## Dev Mode

Set the `DEV_MODE` environment variable to pre-fill all pipeline stages with sample data:

```bash
DEV_MODE=true shiny run app.py
```

This lets any team member jump directly to their tab without needing to run through the upstream modules first.

## Git Branching Strategy

- `main` — stable, always-runnable scaffold
- Each member creates a feature branch:
  - `feature/data-loading`
  - `feature/data-cleaning`
  - `feature/feature-engineering`
  - `feature/eda`
- Since each member edits a separate file under `modules/`, merges should be conflict-free
- After all 4 modules are merged, UI/UX polish happens together on `main`

## Tech Stack

- **Python**: 3.11 (managed via [uv](https://docs.astral.sh/uv/) — auto-downloads the correct version)
- **Environment**: `uv venv --python 3.11` + `uv pip install -r requirements.txt` (creates `.venv/` by default)
- **Framework**: Python Shiny (Core mode) with `@module` decorators
- **UI Theme**: shinyswatch (Bootstrap Flatly)
- **Data**: pandas, numpy
- **ML/Preprocessing**: scikit-learn, statsmodels
- **Visualization**: plotly (interactive), matplotlib + seaborn (static)
- **Deployment**: shinyapps.io via rsconnect-python
