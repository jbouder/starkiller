"""Custom exception classes for Starkiller API."""

from typing import Any


class StarkillerException(Exception):
    """Base exception for Starkiller API."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DataSourceException(StarkillerException):
    """Exception for data source related errors."""

    pass


class DataSourceConnectionError(DataSourceException):
    """Failed to connect to data source."""

    pass


class DataSourceNotFoundError(DataSourceException):
    """Data source not found."""

    pass


class QueryException(StarkillerException):
    """Exception for query related errors."""

    pass


class QueryParseError(QueryException):
    """Failed to parse natural language query."""

    pass


class QueryExecutionError(QueryException):
    """Failed to execute query."""

    pass


class LLMException(StarkillerException):
    """Exception for LLM related errors."""

    pass


class LLMConnectionError(LLMException):
    """Failed to connect to LLM provider."""

    pass


class LLMResponseError(LLMException):
    """Invalid response from LLM provider."""

    pass


class VisualizationException(StarkillerException):
    """Exception for visualization related errors."""

    pass


class VisualizationGenerationError(VisualizationException):
    """Failed to generate visualization."""

    pass


class GenerationException(StarkillerException):
    """Base exception for dashboard generation errors."""

    pass


class GenerationNoDataSourcesError(GenerationException):
    """Dashboard has no associated data sources."""

    pass


class GenerationQueryExecutionError(GenerationException):
    """Failed to execute queries for generation."""

    pass


class GenerationCodeError(GenerationException):
    """Failed to generate React visualization code."""

    pass
