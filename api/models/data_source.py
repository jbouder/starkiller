"""Data source model for storing connection configurations."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from models.query import Query


class DataSource(Base, UUIDMixin, TimestampMixin):
    """Model representing a data source connection."""

    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # csv, postgresql, etc.
    connection_config: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Connection details (encrypted in production)
    schema_info: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Cached schema information
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    queries: Mapped[list["Query"]] = relationship(
        "Query", back_populates="data_source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, name={self.name}, type={self.source_type})>"
