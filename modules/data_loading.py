"""
Data Loading Module — Member 1

Reads: nothing (entry point)
Writes: shared_store.raw_data, shared_store.data_info
"""

import pandas as pd
from shiny import Inputs, Outputs, Session, module, reactive, render, ui

from shared.sample_datasets import BUILTIN_DATASETS


@module.ui
def data_loading_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Load a Dataset"),
            ui.hr(),
            ui.input_select(
                "builtin_dataset",
                "Built-in Datasets",
                choices={"": "— select —", **{k: k.title() for k in BUILTIN_DATASETS}},
            ),
            ui.input_action_button("load_builtin", "Load Built-in Dataset", class_="btn-primary w-100"),
            ui.hr(),
            ui.h5("Or Upload a File"),
            ui.input_file("file_upload", "Choose CSV file", accept=[".csv"]),
            ui.input_action_button("load_file", "Load Uploaded File", class_="btn-outline-primary w-100"),
            width=320,
        ),
        # Main panel
        ui.h4("Dataset Preview"),
        ui.output_ui("dataset_info"),
        ui.output_data_frame("data_preview"),

        # =====================================================================
        # === TODO: ADD YOUR FEATURES BELOW ===
        # Suggested improvements:
        #   - Support more file formats (Excel via openpyxl, JSON, RDS)
        #   - Add file validation and error messages
        #   - Show more dataset metadata (dtypes per column, memory usage)
        # =====================================================================
    )


@module.server
def data_loading_server(input: Inputs, output: Outputs, session: Session, shared_store):

    @reactive.effect
    @reactive.event(input.load_builtin)
    def _load_builtin():
        name = input.builtin_dataset()
        if name and name in BUILTIN_DATASETS:
            df = BUILTIN_DATASETS[name]()
            shared_store.raw_data.set(df)
            shared_store.data_info.set(
                {"filename": f"{name} (built-in)", "rows": df.shape[0], "columns": df.shape[1]}
            )

    @reactive.effect
    @reactive.event(input.load_file)
    def _load_file():
        file_infos = input.file_upload()
        if file_infos:
            file_info = file_infos[0]
            df = pd.read_csv(file_info["datapath"])
            shared_store.raw_data.set(df)
            shared_store.data_info.set(
                {"filename": file_info["name"], "rows": df.shape[0], "columns": df.shape[1]}
            )

    @render.ui
    def dataset_info():
        info = shared_store.data_info()
        if not info:
            return ui.p("No dataset loaded yet. Select a built-in dataset or upload a CSV file.", class_="text-muted")
        return ui.div(
            ui.tags.span(f"Dataset: {info['filename']}", class_="badge bg-success me-2"),
            ui.tags.span(f"Rows: {info['rows']}", class_="badge bg-info me-2"),
            ui.tags.span(f"Columns: {info['columns']}", class_="badge bg-info"),
            class_="mb-3",
        )

    @render.data_frame
    def data_preview():
        df = shared_store.raw_data()
        if df is None:
            return pd.DataFrame()
        return render.DataGrid(df.head(20), filters=True)

    # =========================================================================
    # === TODO: ADD YOUR FEATURES BELOW ===
    # =========================================================================
