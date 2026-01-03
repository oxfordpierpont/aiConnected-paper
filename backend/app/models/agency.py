"""Agency model."""

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Agency(BaseModel):
    """Agency model representing a tenant organization."""

    __tablename__ = "agencies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    subdomain: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    custom_domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#1a4a6e")
    secondary_color: Mapped[str] = mapped_column(String(7), default="#b8860b")

    # Settings
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foreign keys
    plan_id: Mapped[str | None] = mapped_column(
        ForeignKey("plans.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    plan = relationship("Plan", back_populates="agencies")
    users = relationship("User", back_populates="agency", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="agency", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="agency", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="agency", cascade="all, delete-orphan")
