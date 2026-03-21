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
            # ui.output_ui("column_selector_ui"),
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

            ui.h5("Plot Settings"),
            ui.input_select(
                "plot_type",
                "Select Plot Type",
                choices=["Scatter Plot", "Bar Chart (Average)", "Box Plot"]
            ),
            ui.output_ui("column_selector_ui"),

            ui.hr(),
            ui.p(
                "💡 Tip: To download the plot, hover over the top right corner of the chart and click the camera icon ('Download plot as a png').",
                class_="text-muted",
                style="font-size: 0.85em;"
            ),

            width=320,
        ),
        # Main panel
        ui.output_ui("guard_message"),
        ui.navset_card_tab(
            ui.nav_panel(
                "Interactive Plot",
                output_widget("interactive_plot"),
            ),
            ui.nav_panel(
                "Correlation Heatmap",
                output_widget("heatmap_plot"),
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

    # =========================================================================
    # === DYNAMIC UI FOR X AND Y VARIABLES ===
    # =========================================================================

    @render.ui
    def column_selector_ui():
        df = selected_data()
        if df is None:
            return ui.p("No data for this stage", class_="text-muted")

        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not all_cols:
            return ui.p("Dataset is empty", class_="text-warning")

        return ui.TagList(
            ui.input_select("x_var", "X Variable (Feature / Category)", choices=all_cols),
            # The Y-axis typically needs to be numeric; if no numeric type is specified, all columns are used by default.
            ui.input_select("y_var", "Y Variable (Target / Value)", choices=numeric_cols if numeric_cols else all_cols),
            ui.input_select("color_var", "Color / Group By (Optional)", choices=["None"] + all_cols)
        )

    # =========================================================================
    # === PLOTTING LOGIC ===
    # =========================================================================

    @render_widget
    def interactive_plot():
        df = selected_data()
        if df is None:
            return px.scatter(title="No data available")

        x_col = input.x_var()
        y_col = input.y_var()
        plot_type = input.plot_type()
        color_col = input.color_var()

        # Prevent errors from occurring before the UI has finished rendering
        c_val = None if color_col == "None" or color_col not in df.columns else color_col

        if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
            return px.scatter(title="Waiting for variable selection...")

        # Dynamically generate different graphics based on user selection
        if plot_type == "Scatter Plot":
            fig = px.scatter(
                df, x=x_col, y=y_col, color=c_val,
                title=f"Scatter Plot: {y_col} vs {x_col}",
                opacity=0.7
            )
        elif plot_type == "Bar Chart (Average)":
            # Bar chart: Calculate the average value of Y for different values of X
            fig = px.histogram(
                df, x=x_col, y=y_col, color=c_val,
                histfunc='avg',barmode='group',
                title=f"Bar Chart: Average {y_col} by {x_col}"
            )
            fig.update_layout(yaxis_title=f"Average of {y_col}")
        elif plot_type == "Box Plot":
            fig = px.box(
                df, x=x_col, y=y_col, color=c_val,
                title=f"Box Plot: Distribution of {y_col} across {x_col}",
            )

        # Apply chart theme
        fig.update_layout(template="plotly_white")
        return fig

    # =========================================================================
    # === CORRELATION HEATMAP ===
    # =========================================================================

    @render_widget
    def heatmap_plot():
        df = selected_data()
        if df is None:
            return px.imshow([[0]], title="No data available")

        # Extract all numeric variables
        numeric_df = df.select_dtypes(include="number")
        if numeric_df.empty or numeric_df.shape[1] < 2:
            return px.imshow([[0]], title="Not enough numeric columns for heatmap")

        # Calculate the Pearson correlation coefficient
        corr_matrix = numeric_df.corr().round(2)

        # Creating a Heatmap with Plotly
        fig = px.imshow(
            corr_matrix,
            text_auto=True,  # Automatically display values in the cells
            aspect="auto",
            color_continuous_scale="RdBu_r",  # Red-Blue reversed
            title="Correlation Matrix of Numeric Variables"
        )
        fig.update_layout(template="plotly_white")
        return fig

    # =========================================================================
    # === SUMMARY TABLE ===
    # =========================================================================

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
