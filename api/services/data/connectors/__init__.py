"""Data source connectors."""

from typing import Any

from services.data.connectors.base import BaseConnector
from services.data.connectors.postgresql import PostgreSQLConnector


def get_connector(source_type: str, connection_config: dict[str, Any]) -> BaseConnector:
    """
    Get the appropriate connector for a data source type.

    Args:
        source_type: Type of data source (postgresql)
        connection_config: Connection configuration dictionary

    Returns:
        Appropriate connector instance
    """
    connectors = {
        "postgresql": PostgreSQLConnector,
    }

    connector_class = connectors.get(source_type)
    if not connector_class:
        raise ValueError(f"Unknown data source type: {source_type}")

    return connector_class(connection_config)


__all__ = [
    "BaseConnector",
    "PostgreSQLConnector",
    "get_connector",
]
