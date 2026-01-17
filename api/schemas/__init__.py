"""Pydantic request/response schemas."""

from schemas.base import (
    BaseSchema,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
    TimestampSchema,
)
from schemas.data_source import (
    ConnectionConfig,
    DataSourceCreate,
    DataSourceListResponse,
    DataSourceResponse,
    DataSourceTestResponse,
    DataSourceUpdate,
    SchemaColumn,
    SchemaInfo,
    SchemaTable,
)
from schemas.query import (
    QueryHistoryItem,
    QueryHistoryResponse,
    QueryRequest,
    QueryResponse,
    QueryResultData,
)
from schemas.visualization import (
    AxisConfig,
    ChartConfig,
    ChartType,
    DataConfig,
    SeriesConfig,
    VisualizationCreate,
    VisualizationRecommendation,
    VisualizationResponse,
    VisualizationUpdate,
)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampSchema",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    # Data Source
    "ConnectionConfig",
    "DataSourceCreate",
    "DataSourceUpdate",
    "DataSourceResponse",
    "DataSourceListResponse",
    "DataSourceTestResponse",
    "SchemaColumn",
    "SchemaTable",
    "SchemaInfo",
    # Query
    "QueryRequest",
    "QueryResponse",
    "QueryResultData",
    "QueryHistoryItem",
    "QueryHistoryResponse",
    # Visualization
    "ChartType",
    "AxisConfig",
    "SeriesConfig",
    "ChartConfig",
    "DataConfig",
    "VisualizationCreate",
    "VisualizationUpdate",
    "VisualizationResponse",
    "VisualizationRecommendation",
]
