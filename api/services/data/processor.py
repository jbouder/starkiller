"""Data processing utilities using pandas."""

from typing import Any

import pandas as pd

from core.logging import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Utility class for processing data with pandas."""

    @staticmethod
    def dataframe_to_dict(df: pd.DataFrame) -> dict[str, Any]:
        """
        Convert a DataFrame to a dictionary suitable for JSON response.

        Args:
            df: The DataFrame to convert

        Returns:
            Dictionary with columns, rows, and row_count
        """
        # Handle empty DataFrame
        if df.empty:
            return {
                "columns": list(df.columns),
                "rows": [],
                "row_count": 0,
            }

        # Convert DataFrame to records
        rows = df.to_dict(orient="records")

        # Clean up any NaN values
        cleaned_rows = []
        for row in rows:
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned_row[key] = None
                elif isinstance(value, (pd.Timestamp,)):
                    cleaned_row[key] = value.isoformat()
                else:
                    cleaned_row[key] = value
            cleaned_rows.append(cleaned_row)

        return {
            "columns": list(df.columns),
            "rows": cleaned_rows,
            "row_count": len(df),
        }

    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> dict[str, Any]:
        """
        Get a summary of the DataFrame for analysis.

        Args:
            df: The DataFrame to summarize

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": [],
            "memory_usage": df.memory_usage(deep=True).sum(),
        }

        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
            }

            # Add statistics for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = float(df[col].min()) if not df[col].empty else None
                col_info["max"] = float(df[col].max()) if not df[col].empty else None
                col_info["mean"] = float(df[col].mean()) if not df[col].empty else None

            summary["columns"].append(col_info)

        return summary

    @staticmethod
    def apply_transformations(
        df: pd.DataFrame,
        aggregation: str | None = None,
        group_by: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        limit: int | None = None,
    ) -> pd.DataFrame:
        """
        Apply common transformations to a DataFrame.

        Args:
            df: The DataFrame to transform
            aggregation: Aggregation function (sum, avg, count, etc.)
            group_by: Column to group by
            sort_by: Column to sort by
            sort_order: Sort order (asc or desc)
            limit: Maximum number of rows to return

        Returns:
            Transformed DataFrame
        """
        result = df.copy()

        # Group by and aggregate
        if group_by and group_by in result.columns:
            if aggregation:
                agg_funcs = {
                    "sum": "sum",
                    "avg": "mean",
                    "mean": "mean",
                    "count": "count",
                    "min": "min",
                    "max": "max",
                }
                agg_func = agg_funcs.get(aggregation, "sum")

                # Get numeric columns for aggregation
                numeric_cols = result.select_dtypes(include=["number"]).columns
                numeric_cols = [c for c in numeric_cols if c != group_by]

                if numeric_cols:
                    result = result.groupby(group_by)[numeric_cols].agg(agg_func)
                    result = result.reset_index()
            else:
                result = result.groupby(group_by).first().reset_index()

        # Sort
        if sort_by and sort_by in result.columns:
            ascending = sort_order.lower() == "asc"
            result = result.sort_values(by=sort_by, ascending=ascending)

        # Limit
        if limit and limit > 0:
            result = result.head(limit)

        return result
