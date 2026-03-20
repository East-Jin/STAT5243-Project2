"""
Exploratory Data Analysis (EDA) Module — Member 4

Reads: shared_store.raw_data, shared_store.cleaned_data, shared_store.engineered_data
Writes: nothing (read-only analysis)
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from shinywidgets import output_widget, render_widget


@module.ui
def eda_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h4("EDA Controls"),
            ui.hr(),
            ui.input_select(
                "data_stage",
                "Select Data Stage",
                choices={
                    "raw": "Raw Data",
                    "cleaned": "Cleaned Data",
                    "engineered": "Engineered Data",
                },
            ),
            ui.output_ui("column_selector_ui"),
            ui.hr(),

            # =================================================================
            # === TODO: ADD YOUR UI CONTROLS BELOW ===
            # Suggested additions:
            #   - Plot type selector (boxplot, scatter, bar chart)
            #   - Second column selector for bivariate plots
            #   - Correlation heatmap toggle
            #   - Dynamic filtering controls (by column values, ranges)
            #   - Color/grouping column selector
            #   - Distribution fit options (via statsmodels)
            # =================================================================

            width=320,
        ),
        # Main panel
        ui.output_ui("guard_message"),
        ui.navset_card_tab(
            ui.nav_panel(
                "Histogram",
                output_widget("histogram_plot"),
            ),
            ui.nav_panel(
                "Summary Statistics",
                ui.output_data_frame("summary_table"),
            ),
        ),
    )


@module.server
def eda_server(input: Inputs, output: Outputs, session: Session, shared_store):

    # =========================================================================
    # === PREREQUISITE GUARD (DO NOT MODIFY) ===
    # =========================================================================
    @render.ui
    def guard_message():
        if shared_store.raw_data() is None:
            return ui.div(
                ui.div(
                    ui.h4("No data available"),
                    ui.p("Please go to the Data Loading tab and upload or select a dataset first."),
                    class_="alert alert-warning",
                ),
            )
        return ui.TagList()
    # =========================================================================

    @reactive.calc
    def selected_data() -> pd.DataFrame | None:
        stage = input.data_stage()
        if stage == "raw":
            return shared_store.raw_data()
        elif stage == "cleaned":
            return shared_store.cleaned_data()
        elif stage == "engineered":
            return shared_store.engineered_data()
        return None

    @render.ui
    def column_selector_ui():
        df = selected_data()
        if df is None:
            return ui.p("No data for this stage", class_="text-muted")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if not numeric_cols:
            return ui.p("No numeric columns", class_="text-warning")
        return ui.input_select("eda_column", "Select Column", choices=numeric_cols)

    @render_widget
    def histogram_plot():
        df = selected_data()
        if df is None:
            return px.histogram(pd.DataFrame({"empty": []}), title="No data available")
        col = input.eda_column()
        if col not in df.columns:
            return px.histogram(pd.DataFrame({"empty": []}), title="Select a column")
        fig = px.histogram(df, x=col, title=f"Distribution of {col}", marginal="box")
        fig.update_layout(template="plotly_white")
        return fig

    @render.data_frame
    def summary_table():
        df = selected_data()
        if df is None:
            return pd.DataFrame()
        desc = df.describe(include="all").T
        desc.insert(0, "column", desc.index)
        desc = desc.reset_index(drop=True)
        return render.DataGrid(desc, filters=True)

    # =========================================================================
    # === TODO: ADD YOUR FEATURES BELOW ===
    # =========================================================================
