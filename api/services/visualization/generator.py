"""Visualization recommendation and generation service."""

from typing import Any

from core.logging import get_logger
from schemas.visualization import ChartType

logger = get_logger(__name__)


class VisualizationGenerator:
    """Service for generating and recommending visualizations."""

    # Chart type recommendations based on data characteristics
    CHART_TYPE_RULES = {
        "time_series": "line",
        "comparison": "bar",
        "distribution": "pie",
        "trend": "area",
        "correlation": "scatter",
    }

    def analyze_data_characteristics(
        self, columns: list[str], rows: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze data to determine its characteristics for visualization.

        Args:
            columns: List of column names
            rows: List of data rows as dictionaries

        Returns:
            Dictionary with data characteristics
        """
        if not rows:
            return {"type": "empty", "numeric_columns": [], "categorical_columns": []}

        # Analyze column types based on data
        numeric_columns = []
        categorical_columns = []
        date_columns = []

        sample_row = rows[0]
        for col in columns:
            value = sample_row.get(col)
            if value is None:
                continue

            if isinstance(value, (int, float)):
                numeric_columns.append(col)
            elif isinstance(value, str):
                # Check if it looks like a date
                if any(
                    date_indicator in col.lower()
                    for date_indicator in ["date", "time", "year", "month", "day"]
                ):
                    date_columns.append(col)
                else:
                    categorical_columns.append(col)

        # Determine data type
        data_type = "comparison"  # default
        if date_columns:
            data_type = "time_series"
        elif len(numeric_columns) >= 2 and len(categorical_columns) == 0:
            data_type = "correlation"
        elif len(categorical_columns) == 1 and len(numeric_columns) == 1:
            if len(rows) <= 6:
                data_type = "distribution"
            else:
                data_type = "comparison"

        return {
            "type": data_type,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "date_columns": date_columns,
            "row_count": len(rows),
        }

    def suggest_chart_type(self, characteristics: dict[str, Any]) -> ChartType:
        """
        Suggest the best chart type based on data characteristics.

        Args:
            characteristics: Data characteristics from analyze_data_characteristics

        Returns:
            Recommended ChartType
        """
        data_type = characteristics.get("type", "comparison")
        suggested = self.CHART_TYPE_RULES.get(data_type, "bar")
        return suggested  # type: ignore

    def generate_default_config(
        self,
        columns: list[str],
        chart_type: ChartType,
        characteristics: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate a default Recharts-compatible configuration.

        Args:
            columns: List of column names
            chart_type: The chart type to configure
            characteristics: Data characteristics

        Returns:
            Recharts-compatible chart configuration
        """
        numeric_cols = characteristics.get("numeric_columns", [])
        categorical_cols = characteristics.get("categorical_columns", [])
        date_cols = characteristics.get("date_columns", [])

        # Determine x and y axes
        if date_cols:
            x_key = date_cols[0]
        elif categorical_cols:
            x_key = categorical_cols[0]
        else:
            x_key = columns[0] if columns else "x"

        if numeric_cols:
            y_keys = numeric_cols[:3]  # Limit to 3 series
        else:
            y_keys = [columns[1]] if len(columns) > 1 else [columns[0]]

        # Define colors for series
        colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#0088fe"]

        config: dict[str, Any] = {
            "x_axis": {
                "data_key": x_key,
                "label": x_key.replace("_", " ").title(),
            },
            "series": [
                {
                    "data_key": y_key,
                    "name": y_key.replace("_", " ").title(),
                    "color": colors[i % len(colors)],
                }
                for i, y_key in enumerate(y_keys)
            ],
            "legend": len(y_keys) > 1,
            "tooltip": True,
            "grid": True,
        }

        # Add y_axis for non-pie charts
        if chart_type != "pie":
            config["y_axis"] = {
                "data_key": y_keys[0] if y_keys else "value",
                "label": "Value",
            }

        return config

    def to_recharts_format(
        self,
        chart_type: ChartType,
        chart_config: dict[str, Any],
        data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Format configuration and data for Recharts consumption.

        Args:
            chart_type: The chart type
            chart_config: The chart configuration
            data: The data rows

        Returns:
            Recharts-ready configuration with data
        """
        return {
            "type": chart_type,
            "config": chart_config,
            "data": data,
        }
