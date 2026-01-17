"""CSV file data source connector."""

from pathlib import Path
from typing import Any

import pandas as pd

from core.exceptions import DataSourceConnectionError, DataSourceNotFoundError
from core.logging import get_logger
from schemas.data_source import SchemaColumn, SchemaInfo
from services.data.connectors.base import BaseConnector

logger = get_logger(__name__)


class CSVConnector(BaseConnector):
    """Connector for CSV file data sources."""

    def __init__(self, connection_config: dict[str, Any]) -> None:
        super().__init__(connection_config)
        self.file_path = connection_config.get("file_path")
        self._df: pd.DataFrame | None = None

    async def connect(self) -> None:
        """Load the CSV file."""
        if not self.file_path:
            raise DataSourceConnectionError("file_path is required for CSV connector")

        path = Path(self.file_path)
        if not path.exists():
            raise DataSourceNotFoundError(f"CSV file not found: {self.file_path}")

        try:
            self._df = pd.read_csv(self.file_path)
            logger.info("Connected to CSV file", file_path=self.file_path)
        except Exception as e:
            raise DataSourceConnectionError(f"Failed to read CSV file: {str(e)}")

    async def disconnect(self) -> None:
        """Clear the loaded DataFrame."""
        self._df = None

    async def get_schema(self) -> SchemaInfo:
        """Get schema information from the CSV file."""
        if self._df is None:
            await self.connect()

        if self._df is None:
            raise DataSourceConnectionError("Failed to load CSV file")

        columns = []
        for col_name in self._df.columns:
            dtype = str(self._df[col_name].dtype)
            # Map pandas dtypes to generic types
            if "int" in dtype:
                data_type = "integer"
            elif "float" in dtype:
                data_type = "float"
            elif "bool" in dtype:
                data_type = "boolean"
            elif "datetime" in dtype:
                data_type = "datetime"
            else:
                data_type = "string"

            columns.append(
                SchemaColumn(
                    name=col_name,
                    data_type=data_type,
                    nullable=self._df[col_name].isnull().any(),
                )
            )

        return SchemaInfo(columns=columns)

    async def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute pandas code against the loaded DataFrame.

        The query should be valid Python/pandas code that operates on 'df'.
        """
        if self._df is None:
            await self.connect()

        if self._df is None:
            raise DataSourceConnectionError("Failed to load CSV file")

        try:
            # Create a local namespace with the DataFrame
            local_ns: dict[str, Any] = {"df": self._df.copy(), "pd": pd}

            # Execute the pandas code
            exec(query, {"pd": pd}, local_ns)

            # Try to get the result from common variable names
            result = local_ns.get("result", local_ns.get("df", self._df))

            if isinstance(result, pd.Series):
                result = result.to_frame()

            if not isinstance(result, pd.DataFrame):
                # If result is a scalar or something else, wrap it
                result = pd.DataFrame({"result": [result]})

            return result

        except Exception as e:
            logger.error("Query execution failed", error=str(e), query=query)
            raise DataSourceConnectionError(f"Query execution failed: {str(e)}")

    async def get_data(self) -> pd.DataFrame:
        """Get all data from the CSV file."""
        if self._df is None:
            await self.connect()

        if self._df is None:
            raise DataSourceConnectionError("Failed to load CSV file")

        return self._df.copy()
