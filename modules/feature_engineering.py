"""
Feature Engineering Module — Member 3

Reads: shared_store.cleaned_data
Writes: shared_store.engineered_data
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from shiny import Inputs, Outputs, Session, module, reactive, render, ui


@module.ui
def feature_engineering_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Feature Engineering"),
            ui.hr(),
            ui.output_ui("column_selector_ui"),
            ui.input_select(
                "transform_type",
                "Transformation",
                choices={
                    "log": "Log Transform (ln)",
                    "log1p": "Log1p Transform (ln(1+x))",
                    "sqrt": "Square Root",
                },
            ),
            ui.input_action_button("preview_transform", "Preview", class_="btn-outline-info w-100 mb-2"),
            ui.input_action_button("apply_transform", "Apply & Save", class_="btn-primary w-100"),
            ui.hr(),

            # =================================================================
            # === TODO: ADD YOUR UI CONTROLS BELOW ===
            # Suggested additions:
            #   - More transformations (polynomial, power, binning)
            #   - Column combination (add, multiply, ratio of two columns)
            #   - Date/time feature extraction
            #   - Custom formula input
            #   - Undo/history of transformations
            # =================================================================

            width=320,
        ),
        # Main panel
        ui.output_ui("guard_message"),
        ui.h4("Transform Preview"),
        ui.output_data_frame("transform_preview"),
        ui.h4("Current Data"),
        ui.output_data_frame("current_data"),
    )


@module.server
def feature_engineering_server(input: Inputs, output: Outputs, session: Session, shared_store):

    # =========================================================================
    # === PREREQUISITE GUARD (DO NOT MODIFY) ===
    # =========================================================================
    @render.ui
    def guard_message():
        if shared_store.cleaned_data() is None:
            return ui.div(
                ui.div(
                    ui.h4("No cleaned data available"),
                    ui.p("Please go to the Data Cleaning tab and process your data first."),
                    class_="alert alert-warning",
                ),
            )
        return ui.TagList()
    # =========================================================================

    working_copy: reactive.value[pd.DataFrame | None] = reactive.value(None)

    @reactive.effect
    def _sync_cleaned():
        df = shared_store.cleaned_data()
        if df is not None:
            working_copy.set(df.copy())

    @render.ui
    def column_selector_ui():
        df = working_copy()
        if df is None:
            return ui.p("No data available", class_="text-muted")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if not numeric_cols:
            return ui.p("No numeric columns found", class_="text-warning")
        return ui.input_select("target_column", "Select Column", choices=numeric_cols)

    preview_df: reactive.value[pd.DataFrame | None] = reactive.value(None)

    @reactive.effect
    @reactive.event(input.preview_transform)
    def _preview():
        df = working_copy()
        if df is None:
            return
        col = input.target_column()
        transform = input.transform_type()
        if col not in df.columns:
            return

        new_col_name = f"{col}_{transform}"
        result = df.copy()

        if transform == "log":
            result[new_col_name] = np.log(result[col].clip(lower=1e-10))
        elif transform == "log1p":
            result[new_col_name] = np.log1p(result[col])
        elif transform == "sqrt":
            result[new_col_name] = np.sqrt(result[col].clip(lower=0))

        preview_df.set(result)

    @reactive.effect
    @reactive.event(input.apply_transform)
    def _apply():
        df = preview_df()
        if df is not None:
            working_copy.set(df.copy())
            shared_store.engineered_data.set(df.copy())

    @render.data_frame
    def transform_preview():
        df = preview_df()
        if df is None:
            return pd.DataFrame()
        return render.DataGrid(df.tail(10), filters=True)

    @render.data_frame
    def current_data():
        df = working_copy()
        if df is None:
            return pd.DataFrame()
        return render.DataGrid(df.head(20), filters=True)

    # =========================================================================
    # === TODO: ADD YOUR FEATURES BELOW ===
    # =========================================================================
