"""Scheduled content model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ScheduledContent(BaseModel):
    """Scheduled content model for future generations."""

    __tablename__ = "scheduled_content"

    topic: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True, nullable=False
    )  # pending, processing, completed, failed, canceled

    # Generation options
    template_id: Mapped[str | None] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    generation_options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Distribution
    auto_distribute: Mapped[bool] = mapped_column(default=False)
    distribution_platforms: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Result
    document_id: Mapped[str | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    client = relationship("Client", back_populates="scheduled_content")
    template = relationship("Template")
    document = relationship("Document")
    created_by = relationship("User")
