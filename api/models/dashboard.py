"""Dashboard model for grouping visualizations."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from models.data_source import DataSource


# Association table for Dashboard <-> DataSource many-to-many relationship
dashboard_data_sources = Table(
    "dashboard_data_sources",
    Base.metadata,
    Column("dashboard_id", String, ForeignKey("dashboards.id"), primary_key=True),
    Column("data_source_id", String, ForeignKey("data_sources.id"), primary_key=True),
)


class Dashboard(Base, UUIDMixin, TimestampMixin):
    """Model representing a dashboard."""

    __tablename__ = "dashboards"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    data_sources: Mapped[list["DataSource"]] = relationship(
        "DataSource",
        secondary=dashboard_data_sources,
        backref="dashboards",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Dashboard(id={self.id}, title={self.title})>"
