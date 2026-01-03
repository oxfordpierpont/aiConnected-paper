"""Generation job model."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class GenerationJob(BaseModel):
    """Generation job model for tracking content generation."""

    __tablename__ = "generation_jobs"

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True, nullable=False
    )  # pending, researching, writing, rendering, completed, failed

    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Steps detail
    steps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Resource tracking
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    api_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Celery task ID
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Foreign keys
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Relationships
    document = relationship("Document", back_populates="generation_job")
