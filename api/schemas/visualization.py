"""Pydantic schemas for visualization operations."""

from typing import Any, Literal

from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema

ChartType = Literal["line", "bar", "pie", "area", "scatter", "composed"]


class AxisConfig(BaseSchema):
    """Configuration for chart axis."""

    data_key: str
    label: str | None = None
    type: Literal["number", "category"] = "category"


class SeriesConfig(BaseSchema):
    """Configuration for a data series in the chart."""

    data_key: str
    name: str | None = None
    color: str | None = None
    type: Literal["line", "bar", "area"] | None = None  # For composed charts


class ChartConfig(BaseSchema):
    """Recharts-compatible chart configuration."""

    x_axis: AxisConfig
    y_axis: AxisConfig | None = None
    series: list[SeriesConfig]
    legend: bool = True
    tooltip: bool = True
    grid: bool = True


class DataConfig(BaseSchema):
    """Data mapping configuration."""

    aggregation: str | None = None  # sum, avg, count, etc.
    group_by: str | None = None
    sort_by: str | None = None
    sort_order: Literal["asc", "desc"] = "asc"
    limit: int | None = None


class VisualizationCreate(BaseSchema):
    """Schema for creating a visualization."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    chart_type: ChartType
    chart_config: ChartConfig
    data_config: DataConfig = Field(default_factory=DataConfig)
    query_id: str


class VisualizationUpdate(BaseSchema):
    """Schema for updating a visualization."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    chart_type: ChartType | None = None
    chart_config: ChartConfig | None = None
    data_config: DataConfig | None = None
    is_saved: bool | None = None


class VisualizationResponse(TimestampSchema):
    """Schema for visualization response."""

    id: str
    title: str
    description: str | None
    chart_type: ChartType
    chart_config: dict[str, Any]
    data_config: dict[str, Any]
    is_saved: bool
    query_id: str


class VisualizationRecommendation(BaseSchema):
    """Schema for visualization recommendation from LLM."""

    chart_type: ChartType
    title: str
    description: str
    chart_config: ChartConfig
    reasoning: str
