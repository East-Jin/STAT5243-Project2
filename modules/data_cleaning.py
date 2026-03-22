"""
Data Cleaning Module — Member 2

Reads: shared_store.raw_data
Writes: shared_store.cleaned_data
"""

from __future__ import annotations

import re

import matplotlib.pyplot as plt
import pandas as pd
from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from sklearn.preprocessing import MinMaxScaler, StandardScaler


@module.ui
def data_cleaning_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Cleaning Options"),
            ui.hr(),

            # Step 1: Missing-value standardization
            ui.h5("Step 1. Standardize Missing Values"),
            ui.p("Convert empty strings / NA-like tokens to true missing values."),
            ui.input_checkbox("strip_text_before_missing", "Trim whitespace before missing-value check", value=True),
            ui.input_checkbox_group(
                "missing_tokens",
                "Tokens to treat as missing",
                choices={
                    "": '"" (empty string)',
                    " ": '" " (single space)',
                    "NA": "NA",
                    "N/A": "N/A",
                    "na": "na",
                    "null": "null",
                    "NULL": "NULL",
                    "None": "None",
                    "?": "?",
                    "-": "-",
                },
                selected=["", " ", "NA", "N/A", "na", "null", "NULL", "None", "?", "-"],
            ),
            ui.input_action_button(
                "standardize_missing",
                "Apply Missing-Value Standardization",
                class_="btn-outline-primary w-100 mb-2",
            ),
            ui.hr(),

            # Step 2: Missing-value handling
            ui.h5("Step 2. Handle Missing Values"),
            ui.output_ui("missing_summary"),
            ui.input_select(
                "missing_strategy",
                "Missing-value strategy",
                choices={
                    "drop_rows": "Drop rows with any missing values",
                    "drop_cols_threshold": "Drop columns above missing threshold",
                    "impute_mean_median_mode": "Impute numeric + categorical columns",
                },
                selected="drop_rows",
            ),
            ui.input_slider(
                "missing_threshold",
                "Column missing threshold (%)",
                min=0,
                max=100,
                value=50,
                step=5,
            ),
            ui.input_select(
                "numeric_impute",
                "Numeric imputation",
                choices={"mean": "Mean", "median": "Median"},
                selected="median",
            ),
            ui.input_select(
                "categorical_impute",
                "Categorical imputation",
                choices={"mode": "Mode", "unknown": 'Fill with "Unknown"'},
                selected="mode",
            ),
            ui.input_action_button(
                "apply_missing",
                "Apply Missing-Value Handling",
                class_="btn-warning w-100 mb-2",
            ),
            ui.hr(),

            # Step 3: Duplicate handling
            ui.h5("Step 3. Handle Duplicates"),
            ui.output_ui("duplicate_summary"),
            ui.input_action_button(
                "remove_duplicates",
                "Remove Exact Duplicate Rows",
                class_="btn-outline-danger w-100 mb-2",
            ),
            ui.hr(),

            # Step 4: Format standardization
            ui.h5("Step 4. Format Standardization"),
            ui.input_checkbox("standardize_colnames", "Standardize column names", value=True),
            ui.input_checkbox("trim_text", "Trim whitespace in text columns", value=True),
            ui.input_checkbox("lowercase_text", "Convert text columns to lowercase", value=False),
            ui.input_checkbox("try_numeric_conversion", "Try converting text columns to numeric", value=True),
            ui.input_action_button(
                "apply_standardization",
                "Apply Format Standardization",
                class_="btn-outline-secondary w-100 mb-2",
            ),
            ui.hr(),

            # Step 5: Scaling
            ui.h5("Step 5. Scale Numeric Features"),
            ui.input_select(
                "scaling_method",
                "Scaling method",
                choices={
                    "none": "None",
                    "standard": "StandardScaler",
                    "minmax": "MinMaxScaler",
                },
                selected="none",
            ),
            ui.input_action_button(
                "apply_scaling",
                "Apply Scaling",
                class_="btn-outline-primary w-100 mb-2",
            ),
            ui.hr(),

            # Step 6: Encoding
            ui.h5("Step 6. Encode Categorical Features"),
            ui.input_select(
                "encoding_method",
                "Encoding method",
                choices={
                    "none": "None",
                    "onehot": "One-Hot Encoding",
                    "label": "Label Encoding",
                },
                selected="none",
            ),
            ui.input_action_button(
                "apply_encoding",
                "Apply Encoding",
                class_="btn-outline-primary w-100 mb-2",
            ),
            ui.hr(),

            # Step 7: Outlier handling
            ui.h5("Step 7. Handle Outliers"),
            ui.input_select(
                "outlier_method",
                "Outlier method",
                choices={"none": "None", "iqr_remove": "IQR: Remove rows", "iqr_cap": "IQR: Cap values"},
                selected="none",
            ),
            ui.input_action_button(
                "apply_outliers",
                "Apply Outlier Handling",
                class_="btn-outline-danger w-100 mb-2",
            ),
            ui.hr(),

            # Final save
            ui.input_action_button("apply_cleaning", "Apply & Save", class_="btn-primary w-100"),
            width=360,
        ),

        # Main panel
        ui.output_ui("guard_message"),
        ui.output_ui("quality_overview"),

        ui.navset_card_tab(
            ui.nav_panel(
                "Preview",
                ui.output_data_frame("cleaning_preview"),
            ),
            ui.nav_panel(
                "Missing Values",
                ui.output_plot("missing_plot"),
                ui.output_data_frame("missing_table"),
            ),
            ui.nav_panel(
                "Distributions",
                ui.input_select("dist_col", "Select numeric column", choices=[]),
                ui.output_plot("distribution_plot"),
            ),
            ui.nav_panel(
                "Outliers",
                ui.input_select("outlier_col", "Select numeric column", choices=[]),
                ui.output_plot("outlier_plot"),
            ),
            ui.nav_panel(
                "Info",
                ui.output_data_frame("column_info"),
            ),
        ),
        fillable=True,
    )


@module.server
def data_cleaning_server(input: Inputs, output: Outputs, session: Session, shared_store):

    # =========================================================================
    # PREREQUISITE GUARD (DO NOT MODIFY)
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

    # -------------------------------------------------------------------------
    # Helper functions
    # -------------------------------------------------------------------------
    def _get_numeric_cols(df: pd.DataFrame) -> list[str]:
        return df.select_dtypes(include="number").columns.tolist()

    def _get_categorical_cols(df: pd.DataFrame) -> list[str]:
        return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    def _standardize_col_name(name: str) -> str:
        name = str(name).strip().lower()
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^a-z0-9_]", "", name)
        name = re.sub(r"_+", "_", name)
        return name.strip("_")

    # -------------------------------------------------------------------------
    # Sync working copy with raw data
    # -------------------------------------------------------------------------
    @reactive.effect
    def _sync_raw():
        df = shared_store.raw_data()
        if df is not None:
            working_copy.set(df.copy())

    # -------------------------------------------------------------------------
    # Update dynamic select inputs for plots
    # -------------------------------------------------------------------------
    @reactive.effect
    def _update_numeric_selects():
        df = working_copy()
        if df is None:
            ui.update_select("dist_col", choices={}, session=session)
            ui.update_select("outlier_col", choices={}, session=session)
            return

        numeric_cols = _get_numeric_cols(df)
        choices = {col: col for col in numeric_cols}
        selected = numeric_cols[0] if numeric_cols else None

        ui.update_select("dist_col", choices=choices, selected=selected, session=session)
        ui.update_select("outlier_col", choices=choices, selected=selected, session=session)

    # =========================================================================
    # Step 1: Standardize missing-value representation
    # =========================================================================
    @reactive.effect
    @reactive.event(input.standardize_missing)
    def _standardize_missing():
        df = working_copy()
        if df is None:
            return

        df = df.copy()
        selected_tokens = input.missing_tokens()

        for col in df.columns:
            if df[col].dtype == "object" or str(df[col].dtype) == "category":
                df[col] = df[col].astype("object")

                if input.strip_text_before_missing():
                    df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

                df[col] = df[col].replace(selected_tokens, pd.NA)

        working_copy.set(df)
        ui.notification_show("Step 1 done: standardized missing-value tokens.", type="message")

    # =========================================================================
    # Step 2: Handle missing values
    # =========================================================================
    @reactive.effect
    @reactive.event(input.apply_missing)
    def _apply_missing():
        df = working_copy()
        if df is None:
            return

        df = df.copy()
        strategy = input.missing_strategy()
        before_rows = len(df)
        before_cols = len(df.columns)

        if strategy == "drop_rows":
            df = df.dropna().reset_index(drop=True)
            msg = f"Dropped {before_rows - len(df)} rows with missing values."

        elif strategy == "drop_cols_threshold":
            threshold = input.missing_threshold() / 100.0
            missing_ratio = df.isna().mean()
            cols_to_keep = missing_ratio[missing_ratio <= threshold].index.tolist()
            df = df[cols_to_keep].copy()
            msg = f"Dropped {before_cols - len(df.columns)} columns above {input.missing_threshold()}% threshold."

        elif strategy == "impute_mean_median_mode":
            numeric_cols = _get_numeric_cols(df)
            categorical_cols = _get_categorical_cols(df)

            for col in numeric_cols:
                if df[col].isna().any():
                    if input.numeric_impute() == "mean":
                        fill_value = df[col].mean()
                    else:
                        fill_value = df[col].median()
                    df[col] = df[col].fillna(fill_value)

            for col in categorical_cols:
                if df[col].isna().any():
                    if input.categorical_impute() == "mode":
                        mode_series = df[col].mode(dropna=True)
                        fill_value = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                    else:
                        fill_value = "Unknown"
                    df[col] = df[col].fillna(fill_value)
            msg = f"Imputed missing values ({input.numeric_impute()} for numeric, {input.categorical_impute()} for categorical)."
        else:
            msg = "Missing values handled."

        working_copy.set(df)
        ui.notification_show(f"Step 2 done: {msg}", type="message")

    # =========================================================================
    # Step 3: Handle duplicates
    # =========================================================================
    @reactive.effect
    @reactive.event(input.remove_duplicates)
    def _remove_duplicates():
        df = working_copy()
        if df is None:
            return
        before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        removed = before - len(df)
        working_copy.set(df)
        ui.notification_show(f"Step 3 done: removed {removed} duplicate rows.", type="message")

    # =========================================================================
    # Step 4: Format standardization
    # =========================================================================
    @reactive.effect
    @reactive.event(input.apply_standardization)
    def _apply_standardization():
        df = working_copy()
        if df is None:
            return

        df = df.copy()

        if input.standardize_colnames():
            df.columns = [_standardize_col_name(col) for col in df.columns]

        text_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        for col in text_cols:
            df[col] = df[col].astype("object")

            if input.trim_text():
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

            if input.lowercase_text():
                df[col] = df[col].apply(lambda x: x.lower() if isinstance(x, str) else x)

        if input.try_numeric_conversion():
            object_cols = df.select_dtypes(include=["object"]).columns.tolist()
            for col in object_cols:
                converted = pd.to_numeric(df[col], errors="coerce")
                non_missing_original = df[col].notna().sum()
                non_missing_converted = converted.notna().sum()
                if non_missing_original > 0 and non_missing_converted == non_missing_original:
                    df[col] = converted

        working_copy.set(df)
        ui.notification_show("Step 4 done: standardized formats.", type="message")

    # =========================================================================
    # Step 5: Scale numeric features
    # =========================================================================
    @reactive.effect
    @reactive.event(input.apply_scaling)
    def _apply_scaling():
        df = working_copy()
        if df is None:
            return

        method = input.scaling_method()
        if method == "none":
            ui.notification_show("Step 5 skipped: no scaling method selected.", type="warning")
            return

        df = df.copy()
        numeric_cols = _get_numeric_cols(df)

        if not numeric_cols:
            ui.notification_show("Step 5 skipped: no numeric columns available.", type="warning")
            return

        cols_to_scale = [col for col in numeric_cols if not df[col].isna().any()]
        if not cols_to_scale:
            ui.notification_show("Step 5 skipped: all numeric columns have missing values.", type="warning")
            return

        if method == "standard":
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()

        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
        working_copy.set(df)
        ui.notification_show(f"Step 5 done: applied {method} scaling to {len(cols_to_scale)} columns.", type="message")

    # =========================================================================
    # Step 6: Encode categorical features
    # =========================================================================
    @reactive.effect
    @reactive.event(input.apply_encoding)
    def _apply_encoding():
        df = working_copy()
        if df is None:
            return

        method = input.encoding_method()
        if method == "none":
            ui.notification_show("Step 6 skipped: no encoding method selected.", type="warning")
            return

        df = df.copy()
        cat_cols = _get_categorical_cols(df)

        if not cat_cols:
            ui.notification_show("Step 6 skipped: no categorical columns found.", type="warning")
            return

        if method == "onehot":
            df = pd.get_dummies(df, columns=cat_cols, drop_first=False)
        elif method == "label":
            for col in cat_cols:
                df[col] = df[col].astype("category").cat.codes

        working_copy.set(df)
        ui.notification_show(f"Step 6 done: applied {method} encoding to {len(cat_cols)} columns.", type="message")

    # =========================================================================
    # Step 7: Handle outliers
    # =========================================================================
    @reactive.effect
    @reactive.event(input.apply_outliers)
    def _apply_outliers():
        df = working_copy()
        if df is None:
            return

        method = input.outlier_method()
        if method == "none":
            ui.notification_show("Step 7 skipped: no outlier method selected.", type="warning")
            return

        df = df.copy()
        numeric_cols = _get_numeric_cols(df)

        if not numeric_cols:
            ui.notification_show("Step 7 skipped: no numeric columns available.", type="warning")
            return

        before_rows = len(df)

        if method == "iqr_remove":
            keep_mask = pd.Series([True] * len(df), index=df.index)

            for col in numeric_cols:
                series = df[col].dropna()
                if series.empty:
                    continue
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                if iqr == 0:
                    continue
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                col_mask = df[col].isna() | ((df[col] >= lower) & (df[col] <= upper))
                keep_mask = keep_mask & col_mask

            df = df.loc[keep_mask].reset_index(drop=True)
            removed = before_rows - len(df)
            working_copy.set(df)
            ui.notification_show(f"Step 7 done: removed {removed} outlier rows (IQR).", type="message")

        elif method == "iqr_cap":
            for col in numeric_cols:
                series = df[col].dropna()
                if series.empty:
                    continue
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                if iqr == 0:
                    continue
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                df[col] = df[col].clip(lower=lower, upper=upper)

            working_copy.set(df)
            ui.notification_show("Step 7 done: capped outlier values (IQR).", type="message")

    # =========================================================================
    # Final save
    # =========================================================================
    @reactive.effect
    @reactive.event(input.apply_cleaning)
    def _apply():
        df = working_copy()
        if df is not None:
            shared_store.cleaned_data.set(df.copy())
            ui.notification_show(
                f"Cleaned data saved: {df.shape[0]} rows, {df.shape[1]} columns.",
                type="message",
            )

    # =========================================================================
    # Summaries / tables
    # =========================================================================
    @render.ui
    def missing_summary():
        df = working_copy()
        if df is None:
            return ui.p("\u2014", class_="text-muted")

        missing = df.isnull().sum()
        total = int(missing.sum())

        if total == 0:
            return ui.p("No missing values detected.", class_="text-success")

        items = [
            ui.tags.li(f"{col}: {cnt} missing ({df[col].isna().mean():.1%})")
            for col, cnt in missing.items()
            if cnt > 0
        ]
        return ui.div(
            ui.p(f"Total missing cells: {total}", class_="text-danger"),
            ui.tags.ul(items),
        )

    @render.ui
    def duplicate_summary():
        df = working_copy()
        if df is None:
            return ui.p("\u2014", class_="text-muted")

        dup_count = int(df.duplicated().sum())
        dup_pct = dup_count / len(df) if len(df) > 0 else 0

        if dup_count == 0:
            return ui.p("No duplicate rows detected.", class_="text-success")

        return ui.div(
            ui.p(f"Duplicate rows: {dup_count}", class_="text-danger"),
            ui.p(f"Duplicate percentage: {dup_pct:.1%}", class_="text-danger"),
        )

    @render.ui
    def quality_overview():
        df = working_copy()
        if df is None:
            return ui.TagList()

        n_rows, n_cols = df.shape
        missing_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        numeric_cols = len(_get_numeric_cols(df))
        categorical_cols = len(_get_categorical_cols(df))

        return ui.div(
            ui.div(
                ui.tags.span(f"Rows: {n_rows}", class_="badge bg-primary me-2"),
                ui.tags.span(f"Columns: {n_cols}", class_="badge bg-primary me-2"),
                ui.tags.span(f"Missing cells: {missing_cells}", class_="badge bg-warning text-dark me-2"),
                ui.tags.span(f"Duplicate rows: {duplicate_rows}", class_="badge bg-danger me-2"),
                ui.tags.span(f"Numeric cols: {numeric_cols}", class_="badge bg-info me-2"),
                ui.tags.span(f"Categorical cols: {categorical_cols}", class_="badge bg-secondary me-2"),
                class_="mb-1",
            ),
        )

    @render.data_frame
    def cleaning_preview():
        df = working_copy()
        if df is None:
            return pd.DataFrame()
        return render.DataGrid(df, height="100%")

    @render.data_frame
    def missing_table():
        df = working_copy()
        if df is None:
            return pd.DataFrame()

        summary = pd.DataFrame({
            "Column": df.columns,
            "Dtype": [str(df[col].dtype) for col in df.columns],
            "Missing Count": [int(df[col].isna().sum()) for col in df.columns],
            "Missing %": [round(float(df[col].isna().mean() * 100), 2) for col in df.columns],
        })
        return render.DataGrid(summary, height="100%")

    @render.data_frame
    def column_info():
        df = working_copy()
        if df is None:
            return pd.DataFrame()

        info_df = pd.DataFrame({
            "Column": df.columns,
            "Dtype": [str(df[col].dtype) for col in df.columns],
            "Non-Null": [int(df[col].notna().sum()) for col in df.columns],
            "Missing": [int(df[col].isna().sum()) for col in df.columns],
            "Unique": [int(df[col].nunique(dropna=True)) for col in df.columns],
        })
        return render.DataGrid(info_df, height="100%")

    # =========================================================================
    # Plots
    # =========================================================================
    @render.plot
    def missing_plot():
        df = working_copy()
        fig, ax = plt.subplots(figsize=(8, 4))

        if df is None:
            ax.text(0.5, 0.5, "No data loaded", ha="center", va="center")
            ax.axis("off")
            return fig

        missing_counts = df.isna().sum()
        missing_counts = missing_counts[missing_counts > 0]

        if missing_counts.empty:
            ax.text(0.5, 0.5, "No missing values detected", ha="center", va="center")
            ax.axis("off")
            return fig

        missing_counts.sort_values(ascending=False).plot(kind="bar", ax=ax)
        ax.set_title("Missing Values by Column")
        ax.set_xlabel("Column")
        ax.set_ylabel("Missing Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        return fig

    @render.plot
    def distribution_plot():
        df = working_copy()
        fig, ax = plt.subplots(figsize=(8, 4))

        if df is None:
            ax.text(0.5, 0.5, "No data loaded", ha="center", va="center")
            ax.axis("off")
            return fig

        col = input.dist_col()
        if not col or col not in df.columns:
            ax.text(0.5, 0.5, "No numeric column selected", ha="center", va="center")
            ax.axis("off")
            return fig

        series = df[col].dropna()
        if series.empty:
            ax.text(0.5, 0.5, "Selected column has no valid values", ha="center", va="center")
            ax.axis("off")
            return fig

        ax.hist(series, bins=20)
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        plt.tight_layout()
        return fig

    @render.plot
    def outlier_plot():
        df = working_copy()
        fig, ax = plt.subplots(figsize=(8, 4))

        if df is None:
            ax.text(0.5, 0.5, "No data loaded", ha="center", va="center")
            ax.axis("off")
            return fig

        col = input.outlier_col()
        if not col or col not in df.columns:
            ax.text(0.5, 0.5, "No numeric column selected", ha="center", va="center")
            ax.axis("off")
            return fig

        series = df[col].dropna()
        if series.empty:
            ax.text(0.5, 0.5, "Selected column has no valid values", ha="center", va="center")
            ax.axis("off")
            return fig

        ax.boxplot(series, vert=False)
        ax.set_title(f"Boxplot of {col}")
        ax.set_xlabel(col)
        plt.tight_layout()
        return fig
