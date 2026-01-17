"""Base Pydantic schemas and common types."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseSchema):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseSchema, Generic[DataT]):
    """Paginated response wrapper."""

    items: list[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseSchema):
    """Standard error response."""

    error: str
    message: str
    details: dict[str, Any] | None = None


class SuccessResponse(BaseSchema):
    """Standard success response."""

    success: bool = True
    message: str
