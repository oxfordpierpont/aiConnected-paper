"""API key model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class APIKey(BaseModel):
    """API key model for external service credentials."""

    __tablename__ = "api_keys"

    service: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # anthropic, freepik, linkedin, facebook, twitter, google_business

    # Encrypted value
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    agency_id: Mapped[str] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    agency = relationship("Agency", back_populates="api_keys")
