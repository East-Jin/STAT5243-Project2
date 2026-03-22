# STAT5243 Project 2 — Data Explorer

A Python Shiny web application for interactive data loading, cleaning, feature engineering, and exploratory data analysis.

## Quick Start

### 1. Install uv (Python package manager)

We use [uv](https://docs.astral.sh/uv/) to manage the Python environment. It automatically downloads Python 3.11 for you — no global install needed.

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
git clone <repo-url>
cd STAT5243-Project2

# Create a Python 3.11 virtual environment (uv downloads 3.11 automatically)
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

### Dev Mode (for independent module testing)

Pre-fills all pipeline stages with sample data so you can jump to any tab:

```bash
DEV_MODE=true shiny run app.py
```

## Team Member Assignments

| Member | File to Edit | Task |
|--------|-------------|------|
| Member 1 | `modules/data_loading.py` | Dataset upload, format support, validation |
| Member 2 | `modules/data_cleaning.py` | Missing values, duplicates, scaling, encoding |
| Member 3 | `modules/feature_engineering.py` | Transformations, column combinations, feature creation |
| Member 4 | `modules/eda.py` | Interactive visualizations, summary statistics, filtering |

Each file has `TODO` comments marking where to add new features. Look for the `=== TODO: ADD YOUR FEATURES BELOW ===` sections.

## Git Workflow

1. Pull the latest `main`
2. Create your feature branch: `git checkout -b feature/<module-name>`
3. Work on your file in `modules/`
4. Test: `shiny run app.py`
5. Push and create a PR to `main`

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full architecture details, data flow diagrams, and the shared data store contract.

## Deployment (shinyapps.io)

```bash
rsconnect add --account <ACCOUNT> --name <SERVER_NAME> --token <TOKEN> --secret <SECRET>
rsconnect deploy shiny . --name <SERVER_NAME> --title "Data Explorer"
```
