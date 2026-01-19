"""Pydantic schemas for data source operations."""

from typing import Literal

from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema


class ConnectionConfig(BaseSchema):
    """Connection configuration for different data source types."""

    # PostgreSQL specific
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None
    ssl_mode: str | None = None


class DataSourceCreate(BaseSchema):
    """Schema for creating a data source."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    source_type: Literal["postgresql"] = Field(...)
    connection_config: ConnectionConfig = Field(...)


class DataSourceUpdate(BaseSchema):
    """Schema for updating a data source."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    connection_config: ConnectionConfig | None = None
    is_active: bool | None = None


class SchemaColumn(BaseSchema):
    """Schema for a column in a data source."""

    name: str
    data_type: str
    nullable: bool = True


class SchemaTable(BaseSchema):
    """Schema for a table in a data source."""

    name: str
    columns: list[SchemaColumn]


class SchemaInfo(BaseSchema):
    """Schema information for a data source."""

    tables: list[SchemaTable] | None = None


class DataSourceResponse(TimestampSchema):
    """Schema for data source response."""

    id: str
    name: str
    description: str | None
    source_type: str
    schema_info: SchemaInfo | None
    is_active: bool


class DataSourceListResponse(BaseSchema):
    """Schema for listing data sources."""

    items: list[DataSourceResponse]
    total: int


class DataSourceTestResponse(BaseSchema):
    """Schema for data source connection test result."""

    success: bool
    message: str
    schema_info: SchemaInfo | None = None
