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
    ) -> dict[str, Any]:
        """
        Generate a data query from natural language.

        Args:
            natural_language: The user's natural language query
            schema_info: Schema information about the data source
            context: Additional context about the data

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
