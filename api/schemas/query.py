"""Pydantic schemas for query operations."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema
from schemas.visualization import VisualizationResponse


class QueryRequest(BaseSchema):
    """Schema for submitting a natural language query."""

    query: str = Field(..., min_length=1, max_length=2000)
    data_source_id: str | None = None


class QueryResultData(BaseSchema):
    """Schema for query result data."""

    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class QueryResponse(TimestampSchema):
    """Schema for query response."""

    id: str
    natural_language_query: str
    generated_query: str | None
    query_type: str
    status: Literal["pending", "processing", "completed", "failed"]
    result_data: QueryResultData | None
    error_message: str | None
    execution_time_ms: int | None
    data_source_id: str | None
    visualization: VisualizationResponse | None = None


class QueryHistoryItem(BaseSchema):
    """Schema for query history item."""

    id: str
    natural_language_query: str
    status: str
    created_at: datetime
    execution_time_ms: int | None


class QueryHistoryResponse(BaseSchema):
    """Schema for query history response."""

    items: list[QueryHistoryItem]
    total: int
