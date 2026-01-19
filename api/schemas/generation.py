"""Pydantic schemas for dashboard generation operations."""

from typing import Any, Literal

from pydantic import Field

from schemas.base import BaseSchema


class VisualizationPreferences(BaseSchema):
    """Preferences for generated visualizations."""

    chart_types: list[Literal["line", "bar", "pie", "area", "scatter", "composed"]] | None = None
    color_scheme: str | None = None
    layout: Literal["grid", "stacked", "single"] | None = None


class GenerateRequest(BaseSchema):
    """Request schema for dashboard generation."""

    query: str | None = Field(
        None,
        description="Optional natural language query to augment dashboard description",
    )
    visualization_preferences: VisualizationPreferences | None = None


class GeneratedComponent(BaseSchema):
    """Metadata for a generated visualization component."""

    name: str
    chart_type: str
    description: str
    data_keys: list[str]


class GeneratedQuery(BaseSchema):
    """Information about a query executed for a data source."""

    data_source_id: str
    data_source_name: str
    query: str
    query_type: str
    row_count: int


class DataSourceTiming(BaseSchema):
    """Timing breakdown for a single data source processing."""

    data_source_id: str
    data_source_name: str
    schema_retrieval_ms: int = Field(description="Time to fetch schema from database")
    llm_query_generation_ms: int = Field(description="Time for LLM to generate SQL query")
    query_execution_ms: int = Field(description="Time to execute the generated query")
    data_processing_ms: int = Field(description="Time to process query results")
    total_ms: int = Field(description="Total time for this data source")


class TimingMetrics(BaseSchema):
    """Detailed timing breakdown for dashboard generation."""

    dashboard_fetch_ms: int = Field(description="Time to fetch dashboard from database")
    data_source_timings: list[DataSourceTiming] = Field(
        default_factory=list,
        description="Per-data-source timing breakdown",
    )
    total_data_sources_ms: int = Field(
        description="Total time spent processing all data sources"
    )
    llm_visualization_ms: int = Field(
        description="Time for LLM to generate React visualization code"
    )
    response_assembly_ms: int = Field(description="Time to assemble final response")
    total_ms: int = Field(description="Total generation time")


class GenerateResponse(BaseSchema):
    """Response schema for dashboard generation."""

    dashboard_id: str
    dashboard_title: str
    react_code: str
    components: list[GeneratedComponent]
    data_sources_used: list[str]
    queries_generated: list[GeneratedQuery]
    sample_data: dict[str, Any]
    execution_time_ms: int
    timing_metrics: TimingMetrics | None = Field(
        default=None,
        description="Detailed timing breakdown for performance analysis",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
