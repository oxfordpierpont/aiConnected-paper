"""Client model."""

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Client(BaseModel):
    """Client model representing an agency's customer (seat)."""

    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Content preferences
    services: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tone: Mapped[str] = mapped_column(String(50), default="professional")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foreign keys
    agency_id: Mapped[str] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    agency = relationship("Agency", back_populates="clients")
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    scheduled_content = relationship(
        "ScheduledContent", back_populates="client", cascade="all, delete-orphan"
    )
