"""
Feature Engineering Module — Member 3

Reads: shared_store.cleaned_data
Writes: shared_store.engineered_data
"""


from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from shinywidgets import output_widget, render_widget


@module.ui
def feature_engineering_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Feature Engineering"),
            ui.hr(),

            ui.h5("Choose Operation Type"),
            ui.input_select(
                "operation_type",
                "Operation Category",
                choices={
                    "single": "Single-Column Transformation",
                    "combine": "Combine Two Columns",
                    "datetime": "Date / Time Extraction",
                },
            ),

            ui.output_ui("column_selector_ui"),
            ui.output_ui("operation_controls_ui"),

            ui.hr(),
            ui.input_text(
                "custom_feature_name",
                "Custom Feature Name (optional)",
                placeholder="Leave blank to auto-generate",
            ),

            ui.input_action_button(
                "preview_transform",
                "Preview",
                class_="btn-outline-info w-100 mb-2",
            ),
            ui.input_action_button(
                "apply_transform",
                "Apply & Save",
                class_="btn-primary w-100 mb-2",
            ),
            ui.input_action_button(
                "reset_features",
                "Reset to Cleaned Data",
                class_="btn-warning w-100",
            ),

            ui.hr(),
            ui.p(
                "Tip: Preview lets you inspect the new feature before saving it to engineered data.",
                class_="text-muted",
                style="font-size: 0.9em;",
            ),
            width=340,
        ),

        ui.output_ui("guard_message"),

        ui.navset_card_tab(
            ui.nav_panel(
                "Preview Table",
                ui.h4("Transform Preview"),
                ui.output_ui("status_message"),
                ui.output_data_frame("transform_preview"),
            ),
            ui.nav_panel(
                "Current Data",
                ui.h4("Current Working Data"),
                ui.output_data_frame("current_data"),
            ),
            ui.nav_panel(
                "Visual Feedback",
                ui.h4("Before / After Distribution"),
                output_widget("before_plot"),
                ui.br(),
                output_widget("after_plot"),
            ),
            ui.nav_panel(
                "Feature History",
                ui.h4("Created Features"),
                ui.output_ui("feature_history"),
            ),
        ),
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
    preview_df: reactive.value[pd.DataFrame | None] = reactive.value(None)
    preview_meta: reactive.value[dict] = reactive.value({})
    feature_history_store: reactive.value[list[str]] = reactive.value([])
    status_store: reactive.value[str] = reactive.value("")

    @reactive.effect
    def _sync_cleaned():
        df = shared_store.cleaned_data()
        if df is not None:
            working_copy.set(df.copy())
            preview_df.set(None)
            preview_meta.set({})
            feature_history_store.set([])
            status_store.set("Working copy synced from cleaned data.")

    @reactive.effect
    @reactive.event(input.reset_features)
    def _reset_features():
        df = shared_store.cleaned_data()
        if df is not None:
            working_copy.set(df.copy())
            preview_df.set(None)
            preview_meta.set({})
            feature_history_store.set([])
            shared_store.engineered_data.set(df.copy())
            status_store.set("Reset complete. Working data restored to cleaned data.")

    @render.ui
    def column_selector_ui():
        df = working_copy()
        if df is None:
            return ui.p("No data available", class_="text-muted")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if input.operation_type() == "single":
            if not numeric_cols:
                return ui.p("No numeric columns found.", class_="text-warning")
            return ui.input_select(
                "target_column",
                "Select Numeric Column",
                choices=numeric_cols,
            )

        if input.operation_type() == "datetime":
            dt_cols = _datetime_candidate_columns(df)
            if not dt_cols:
                return ui.p(
                    "No datetime columns found, and no text column parsed as dates. "
                    "Load data with a datetime column or date strings.",
                    class_="text-warning",
                )
            return ui.input_select(
                "datetime_column",
                "Date / Time Column",
                choices=dt_cols,
            )

        if len(numeric_cols) < 2:
            return ui.p("At least two numeric columns are required for combination features.", class_="text-warning")

        return ui.TagList(
            ui.input_select("first_column", "First Numeric Column", choices=numeric_cols),
            ui.input_select("second_column", "Second Numeric Column", choices=numeric_cols),
        )

    @render.ui
    def operation_controls_ui():
        if input.operation_type() == "single":
            return ui.TagList(
                ui.input_select(
                    "transform_type",
                    "Transformation",
                    choices={
                        "log": "Log Transform (ln)",
                        "log1p": "Log1p Transform (ln(1+x))",
                        "sqrt": "Square Root",
                        "square": "Square",
                        "zscore": "Standardization (Z-score)",
                        "minmax": "Min-Max Scaling",
                        "binning": "Binning",
                    },
                ),
                ui.output_ui("binning_ui"),
            )

        if input.operation_type() == "datetime":
            return ui.input_select(
                "datetime_part",
                "Extract",
                choices={
                    "year": "Calendar year",
                    "month": "Month (1–12)",
                    "day": "Day of month",
                    "dayofweek": "Day of week (0=Mon … 6=Sun)",
                    "hour": "Hour (0–23)",
                    "minute": "Minute (0–59)",
                    "quarter": "Quarter (1–4)",
                    "is_weekend": "Is weekend (1=yes, 0=no)",
                    "dayofyear": "Day of year (1–366)",
                },
            )

        return ui.input_select(
            "combine_type",
            "Combination Method",
            choices={
                "add": "Add (x1 + x2)",
                "multiply": "Multiply (x1 × x2)",
                "ratio": "Ratio (x1 / x2)",
            },
        )

    @render.ui
    def binning_ui():
        if input.operation_type() == "single" and input.transform_type() == "binning":
            return ui.input_slider(
                "num_bins",
                "Number of Bins",
                min=2,
                max=10,
                value=4,
            )
        return ui.TagList()

    def _datetime_candidate_columns(df: pd.DataFrame) -> list[str]:
        """Columns that are datetimes or object/strings that may parse as dates."""
        out: list[str] = []
        for c in df.columns:
            s = df[c]
            if pd.api.types.is_datetime64_any_dtype(s):
                out.append(c)
            elif s.dtype == object or pd.api.types.is_string_dtype(s):
                sample = s.dropna().head(50)
                if len(sample) == 0:
                    continue
                parsed = pd.to_datetime(sample, errors="coerce")
                if parsed.notna().sum() >= max(1, len(sample) // 2):
                    out.append(c)
        return out

    def _series_as_datetime(series: pd.Series) -> pd.Series:
        if pd.api.types.is_datetime64_any_dtype(series):
            return series
        return pd.to_datetime(series, errors="coerce")

    def _safe_feature_name(default_name: str) -> str:
        custom_name = input.custom_feature_name().strip()
        return custom_name if custom_name else default_name

    @reactive.effect
    @reactive.event(input.preview_transform)
    def _preview():
        df = working_copy()
        if df is None:
            status_store.set("No data available.")
            return

        result = df.copy()

        try:
            if input.operation_type() == "single":
                col = input.target_column()
                transform = input.transform_type()

                if col not in result.columns:
                    status_store.set("Selected column not found.")
                    return

                if transform == "log":
                    new_col_name = _safe_feature_name(f"{col}_log")
                    result[new_col_name] = np.log(result[col].clip(lower=1e-10))

                elif transform == "log1p":
                    new_col_name = _safe_feature_name(f"{col}_log1p")
                    result[new_col_name] = np.log1p(result[col].clip(lower=0))

                elif transform == "sqrt":
                    new_col_name = _safe_feature_name(f"{col}_sqrt")
                    result[new_col_name] = np.sqrt(result[col].clip(lower=0))

                elif transform == "square":
                    new_col_name = _safe_feature_name(f"{col}_square")
                    result[new_col_name] = np.square(result[col])

                elif transform == "zscore":
                    new_col_name = _safe_feature_name(f"{col}_zscore")
                    std = result[col].std()
                    if std == 0 or pd.isna(std):
                        status_store.set(f"Cannot standardize '{col}' because its standard deviation is 0.")
                        return
                    result[new_col_name] = (result[col] - result[col].mean()) / std

                elif transform == "minmax":
                    new_col_name = _safe_feature_name(f"{col}_minmax")
                    col_min = result[col].min()
                    col_max = result[col].max()
                    if col_min == col_max:
                        status_store.set(f"Cannot min-max scale '{col}' because all values are identical.")
                        return
                    result[new_col_name] = (result[col] - col_min) / (col_max - col_min)

                elif transform == "binning":
                    bins = input.num_bins()
                    new_col_name = _safe_feature_name(f"{col}_binned")
                    result[new_col_name] = pd.cut(result[col], bins=bins, include_lowest=True).astype(str)

                else:
                    status_store.set("Unknown transformation selected.")
                    return

                preview_meta.set(
                    {
                        "mode": "single",
                        "source_col": col,
                        "new_col": new_col_name,
                    }
                )
                preview_df.set(result)
                status_store.set(f"Preview created: {new_col_name}")

            elif input.operation_type() == "datetime":
                col = input.datetime_column()
                part = input.datetime_part()

                if col not in result.columns:
                    status_store.set("Selected date/time column not found.")
                    return

                ts = _series_as_datetime(result[col])
                valid = ts.notna().sum()
                if valid == 0:
                    status_store.set(f"Could not parse '{col}' as dates. Check values or use a datetime column.")
                    return
                parse_note = ""
                if valid < len(ts) * 0.5:
                    parse_note = f" — parsed {valid}/{len(ts)} rows as dates."

                suffix = {
                    "year": "year",
                    "month": "month",
                    "day": "day",
                    "dayofweek": "dow",
                    "hour": "hour",
                    "minute": "minute",
                    "quarter": "quarter",
                    "is_weekend": "weekend",
                    "dayofyear": "doy",
                }.get(part, part)
                default_name = f"{col}_{suffix}"
                new_col_name = _safe_feature_name(default_name)

                if part == "year":
                    new_vals = ts.dt.year
                elif part == "month":
                    new_vals = ts.dt.month
                elif part == "day":
                    new_vals = ts.dt.day
                elif part == "dayofweek":
                    new_vals = ts.dt.dayofweek
                elif part == "hour":
                    new_vals = ts.dt.hour
                elif part == "minute":
                    new_vals = ts.dt.minute
                elif part == "quarter":
                    new_vals = ts.dt.quarter
                elif part == "is_weekend":
                    new_vals = ts.dt.dayofweek.isin([5, 6]).astype(int)
                elif part == "dayofyear":
                    new_vals = ts.dt.dayofyear
                else:
                    status_store.set("Unknown date/time part selected.")
                    return

                result[new_col_name] = new_vals
                preview_meta.set(
                    {
                        "mode": "datetime",
                        "source_col": col,
                        "new_col": new_col_name,
                        "datetime_part": part,
                    }
                )
                preview_df.set(result)
                status_store.set(f"Preview created: {new_col_name}{parse_note}")

            else:
                col1 = input.first_column()
                col2 = input.second_column()
                combine_type = input.combine_type()

                if col1 not in result.columns or col2 not in result.columns:
                    status_store.set("Selected columns not found.")
                    return

                if combine_type == "add":
                    new_col_name = _safe_feature_name(f"{col1}_plus_{col2}")
                    result[new_col_name] = result[col1] + result[col2]

                elif combine_type == "multiply":
                    new_col_name = _safe_feature_name(f"{col1}_times_{col2}")
                    result[new_col_name] = result[col1] * result[col2]

                elif combine_type == "ratio":
                    new_col_name = _safe_feature_name(f"{col1}_div_{col2}")
                    denominator = result[col2].replace(0, np.nan)
                    result[new_col_name] = result[col1] / denominator

                else:
                    status_store.set("Unknown combination selected.")
                    return

                preview_meta.set(
                    {
                        "mode": "combine",
                        "source_col": col1,
                        "second_col": col2,
                        "new_col": new_col_name,
                    }
                )
                preview_df.set(result)
                status_store.set(f"Preview created: {new_col_name}")

        except Exception as e:
            status_store.set(f"Preview failed: {str(e)}")

    @reactive.effect
    @reactive.event(input.apply_transform)
    def _apply():
        df = preview_df()
        meta = preview_meta()

        if df is None or not meta:
            status_store.set("Nothing to apply. Please create a preview first.")
            return

        working_copy.set(df.copy())
        shared_store.engineered_data.set(df.copy())

        history = feature_history_store().copy()
        new_feature = meta.get("new_col")
        if new_feature and new_feature not in history:
            history.append(new_feature)
            feature_history_store.set(history)

        status_store.set(f"Applied and saved to engineered data: {new_feature}")

    @render.ui
    def status_message():
        msg = status_store()
        if not msg:
            return ui.TagList()
        return ui.div(msg, class_="alert alert-info")

    @render.data_frame
    def transform_preview():
        df = preview_df()
        if df is None:
            return pd.DataFrame()
        meta = preview_meta()
        if meta and meta.get("new_col") in df.columns:
            cols_to_show = [meta.get("source_col"), meta.get("new_col")]
            if meta.get("mode") == "combine":
                cols_to_show = [meta.get("source_col"), meta.get("second_col"), meta.get("new_col")]
            cols_to_show = [c for c in cols_to_show if c in df.columns]
            return render.DataGrid(df[cols_to_show].head(20), filters=True)
        return render.DataGrid(df.head(20), filters=True)

    @render.data_frame
    def current_data():
        df = working_copy()
        if df is None:
            return pd.DataFrame()
        return render.DataGrid(df.head(20), filters=True)

    @render_widget
    def before_plot():
        df = working_copy()
        meta = preview_meta()

        if df is None or not meta:
            return px.histogram(title="Create a preview to see visual feedback.")

        source_col = meta.get("source_col")
        if source_col not in df.columns:
            return px.histogram(title="Source column not found.")

        if meta.get("mode") == "datetime":
            ts = _series_as_datetime(df[source_col])
            tdf = pd.DataFrame({"time": ts.dropna()})
            if tdf.empty:
                return px.histogram(title="No parseable dates for plotting.")
            fig = px.histogram(
                tdf,
                x="time",
                nbins=30,
                title=f"Before: {source_col} (parsed timeline)",
            )
            fig.update_layout(template="plotly_white")
            return fig

        if not pd.api.types.is_numeric_dtype(df[source_col]):
            return px.histogram(title="No numeric source column available for plotting.")

        fig = px.histogram(
            df,
            x=source_col,
            nbins=20,
            title=f"Before: {source_col}",
        )
        fig.update_layout(template="plotly_white")
        return fig

    @render_widget
    def after_plot():
        df = preview_df()
        meta = preview_meta()

        if df is None or not meta:
            return px.histogram(title="Create a preview to see visual feedback.")

        new_col = meta.get("new_col")
        if new_col not in df.columns:
            return px.histogram(title="Preview feature not found.")

        if pd.api.types.is_numeric_dtype(df[new_col]):
            fig = px.histogram(
                df,
                x=new_col,
                nbins=20,
                title=f"After: {new_col}",
            )
        else:
            counts = df[new_col].value_counts(dropna=False).reset_index()
            counts.columns = [new_col, "count"]
            fig = px.bar(
                counts,
                x=new_col,
                y="count",
                title=f"After: {new_col}",
            )

        fig.update_layout(template="plotly_white")
        return fig

    @render.ui
    def feature_history():
        history = feature_history_store()
        if not history:
            return ui.p("No engineered features have been saved yet.", class_="text-muted")
        return ui.tags.ul([ui.tags.li(name) for name in history])