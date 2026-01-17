"""Query model for storing query history and results."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from models.data_source import DataSource
    from models.visualization import Visualization


class Query(Base, UUIDMixin, TimestampMixin):
    """Model representing a natural language query and its results."""

    __tablename__ = "queries"

    natural_language_query: Mapped[str] = mapped_column(Text, nullable=False)
    generated_query: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # SQL or pandas code
    query_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="sql"
    )  # sql, pandas, etc.
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, processing, completed, failed
    result_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Query result data
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(nullable=True)

    # Foreign keys
    data_source_id: Mapped[str | None] = mapped_column(
        ForeignKey("data_sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    data_source: Mapped["DataSource | None"] = relationship(
        "DataSource", back_populates="queries"
    )
    visualization: Mapped["Visualization | None"] = relationship(
        "Visualization", back_populates="query", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Query(id={self.id}, status={self.status})>"
