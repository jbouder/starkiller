"""Pydantic schemas for dashboard operations."""

from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema
from schemas.data_source import DataSourceResponse


class DashboardBase(BaseSchema):
    """Base schema for dashboard."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class DashboardCreate(DashboardBase):
    """Schema for creating a dashboard."""

    data_source_ids: list[str] = Field(default_factory=list)


class DashboardUpdate(BaseSchema):
    """Schema for updating a dashboard."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    data_source_ids: list[str] | None = None


class DashboardResponse(DashboardBase, TimestampSchema):
    """Schema for dashboard response."""

    id: str
    data_sources: list[DataSourceResponse]
