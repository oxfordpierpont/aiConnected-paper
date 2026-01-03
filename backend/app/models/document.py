"""Document model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Document(BaseModel):
    """Document model for generated content."""

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="draft", index=True, nullable=False
    )  # draft, generating, ready, distributed, failed

    # Generated content
    content_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Metadata
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    statistics_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sources_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Generation settings
    template_id: Mapped[str | None] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    generation_options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Distribution
    distribution_status: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Expiry
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    agency_id: Mapped[str] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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
    agency = relationship("Agency", back_populates="documents")
    client = relationship("Client", back_populates="documents")
    template = relationship("Template")
    created_by = relationship("User")
    generation_job = relationship(
        "GenerationJob", back_populates="document", uselist=False
    )
