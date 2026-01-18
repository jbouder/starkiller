"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM provider implementations."""

    @abstractmethod
    async def generate_query(
        self,
        natural_language: str,
        schema_info: dict[str, Any],
        context: str | None = None,
        source_type: str = "csv",
    ) -> dict[str, Any]:
        """
        Generate a data query from natural language.

        Args:
            natural_language: The user's natural language query
            schema_info: Schema information about the data source
            context: Additional context about the data
            source_type: Type of data source ("postgresql" for SQL, "csv" for pandas)

        Returns:
            Dictionary containing:
                - query: The generated query (SQL, pandas code, etc.)
                - query_type: Type of query generated
                - explanation: Explanation of what the query does
        """
        pass

    @abstractmethod
    async def recommend_visualization(
        self,
        query_result: dict[str, Any],
        natural_language: str,
    ) -> dict[str, Any]:
        """
        Recommend a visualization for query results.

        Args:
            query_result: The data returned from the query
            natural_language: The original natural language query

        Returns:
            Dictionary containing:
                - chart_type: Recommended chart type
                - title: Suggested title
                - description: Description of the visualization
                - chart_config: Recharts-compatible configuration
                - reasoning: Why this visualization was chosen
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM provider is available.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def generate_react_visualization(
        self,
        dashboard_context: dict[str, Any],
        data_samples: list[dict[str, Any]],
        preferences: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate React visualization code for a dashboard.

        Args:
            dashboard_context: Dashboard title, description, and schema info
            data_samples: Sample data from each data source
            preferences: Optional visualization preferences

        Returns:
            Dictionary containing:
                - react_code: Complete exportable React Dashboard component
                - components: Array of component metadata
                - reasoning: Design decision explanation
        """
        pass
