"""Abstract base class for data source connectors."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from schemas.data_source import SchemaInfo


class BaseConnector(ABC):
    """Abstract base class for data source connector implementations."""

    def __init__(self, connection_config: dict[str, Any]) -> None:
        self.connection_config = connection_config

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source."""
        pass

    @abstractmethod
    async def get_schema(self) -> SchemaInfo:
        """
        Retrieve schema information from the data source.

        Returns:
            SchemaInfo containing tables/columns information
        """
        pass

    @abstractmethod
    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a query against the data source.

        Args:
            query: The query to execute (SQL or pandas code)

        Returns:
            DataFrame containing the query results
        """
        pass

    @abstractmethod
    async def get_data(self) -> pd.DataFrame:
        """
        Get all data from the data source.

        Returns:
            DataFrame containing the data
        """
        pass

    async def __aenter__(self) -> "BaseConnector":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()
