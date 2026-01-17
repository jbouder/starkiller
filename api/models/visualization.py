"""Visualization model for storing visualization configurations."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from models.query import Query


class Visualization(Base, UUIDMixin, TimestampMixin):
    """Model representing a saved visualization configuration."""

    __tablename__ = "visualizations"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    chart_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # line, bar, pie, area, scatter, etc.
    chart_config: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Recharts-compatible configuration
    data_config: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # Data mapping configuration
    is_saved: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Foreign keys
    query_id: Mapped[str] = mapped_column(
        ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    query: Mapped["Query"] = relationship("Query", back_populates="visualization")

    def __repr__(self) -> str:
        return f"<Visualization(id={self.id}, title={self.title}, type={self.chart_type})>"
