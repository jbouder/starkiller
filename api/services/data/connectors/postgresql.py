"""PostgreSQL data source connector."""

from typing import Any

import pandas as pd

from core.exceptions import DataSourceConnectionError
from core.logging import get_logger
from schemas.data_source import SchemaColumn, SchemaInfo, SchemaTable
from services.data.connectors.base import BaseConnector

logger = get_logger(__name__)


class PostgreSQLConnector(BaseConnector):
    """Connector for PostgreSQL data sources."""

    def __init__(self, connection_config: dict[str, Any]) -> None:
        super().__init__(connection_config)
        self.host = connection_config.get("host", "localhost")
        self.port = connection_config.get("port", 5432)
        self.database = connection_config.get("database")
        self.username = connection_config.get("username")
        self.password = connection_config.get("password")
        self.ssl_mode = connection_config.get("ssl_mode", "prefer")
        self._connection_string: str | None = None

    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string."""
        if not self.database:
            raise DataSourceConnectionError("database is required")
        if not self.username:
            raise DataSourceConnectionError("username is required")

        password_part = f":{self.password}" if self.password else ""
        return f"postgresql://{self.username}{password_part}@{self.host}:{self.port}/{self.database}"

    async def connect(self) -> None:
        """Establish connection to PostgreSQL."""
        try:
            self._connection_string = self._build_connection_string()
            # Test connection by trying to read
            logger.info(
                "PostgreSQL connection configured",
                host=self.host,
                database=self.database,
            )
        except Exception as e:
            raise DataSourceConnectionError(f"Failed to connect: {str(e)}")

    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        self._connection_string = None

    async def get_schema(self) -> SchemaInfo:
        """Get schema information from PostgreSQL."""
        if not self._connection_string:
            await self.connect()

        try:
            # Query to get table and column information
            schema_query = """
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """

            df = pd.read_sql(schema_query, self._connection_string)

            tables_dict: dict[str, list[SchemaColumn]] = {}
            for _, row in df.iterrows():
                table_name = row["table_name"]
                if table_name not in tables_dict:
                    tables_dict[table_name] = []

                tables_dict[table_name].append(
                    SchemaColumn(
                        name=row["column_name"],
                        data_type=row["data_type"],
                        nullable=row["is_nullable"] == "YES",
                    )
                )

            tables = [
                SchemaTable(name=name, columns=cols)
                for name, cols in tables_dict.items()
            ]

            return SchemaInfo(tables=tables)

        except Exception as e:
            logger.error("Failed to get schema", error=str(e))
            raise DataSourceConnectionError(f"Failed to get schema: {str(e)}")

    async def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query against PostgreSQL."""
        if not self._connection_string:
            await self.connect()

        try:
            df = pd.read_sql(query, self._connection_string)
            return df
        except Exception as e:
            logger.error("Query execution failed", error=str(e))
            raise DataSourceConnectionError(f"Query execution failed: {str(e)}")

    async def get_data(self) -> pd.DataFrame:
        """Get data - not directly supported for PostgreSQL without table specification."""
        raise DataSourceConnectionError(
            "get_data() requires a table name for PostgreSQL. Use execute_query() instead."
        )
