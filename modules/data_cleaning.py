"""
Data Cleaning Module — Member 2

Reads: shared_store.raw_data
Writes: shared_store.cleaned_data
"""

from __future__ import annotations

import pandas as pd
from shiny import Inputs, Outputs, Session, module, reactive, render, ui


@module.ui
def data_cleaning_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Cleaning Options"),
            ui.hr(),
            ui.h5("Missing Values"),
            ui.output_ui("missing_summary"),
            ui.input_action_button("drop_na", "Drop Rows with NaN", class_="btn-warning w-100 mb-2"),
            ui.input_action_button("apply_cleaning", "Apply & Save", class_="btn-primary w-100"),
            ui.hr(),

            # =================================================================
            # === TODO: ADD YOUR UI CONTROLS BELOW ===
            # Suggested additions:
            #   - Imputation strategy selector (mean, median, mode, custom)
            #   - Duplicate detection and removal button
            #   - Scaling options (StandardScaler, MinMaxScaler)
            #   - Categorical encoding (one-hot, label encoding)
            #   - Outlier detection controls
            # =================================================================

            width=320,
        ),
        # Main panel
        ui.output_ui("guard_message"),
        ui.h4("Data Preview (working copy)"),
        ui.output_data_frame("cleaning_preview"),
    )


@module.server
def data_cleaning_server(input: Inputs, output: Outputs, session: Session, shared_store):

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

    working_copy: reactive.value[pd.DataFrame | None] = reactive.value(None)

    @reactive.effect
    def _sync_raw():
        """Keep working copy in sync with raw_data when it changes."""
        df = shared_store.raw_data()
        if df is not None:
            working_copy.set(df.copy())

    @reactive.effect
    @reactive.event(input.drop_na)
    def _drop_na():
        df = working_copy()
        if df is not None:
            working_copy.set(df.dropna().reset_index(drop=True))

    @reactive.effect
    @reactive.event(input.apply_cleaning)
    def _apply():
        df = working_copy()
        if df is not None:
            shared_store.cleaned_data.set(df.copy())

    @render.ui
    def missing_summary():
        df = working_copy()
        if df is None:
            return ui.p("—", class_="text-muted")
        missing = df.isnull().sum()
        total = int(missing.sum())
        if total == 0:
            return ui.p("No missing values detected.", class_="text-success")
        items = [ui.tags.li(f"{col}: {cnt} missing") for col, cnt in missing.items() if cnt > 0]
        return ui.div(
            ui.p(f"Total missing cells: {total}", class_="text-danger"),
            ui.tags.ul(items),
        )

    @render.data_frame
    def cleaning_preview():
        df = working_copy()
        if df is None:
            return pd.DataFrame()
        return render.DataGrid(df.head(20), filters=True)

    # =========================================================================
    # === TODO: ADD YOUR FEATURES BELOW ===
    # =========================================================================
