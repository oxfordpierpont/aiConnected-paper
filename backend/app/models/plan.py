"""Plan model."""

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Plan(BaseModel):
    """Plan model for subscription tiers."""

    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pricing
    price_monthly: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_yearly: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Limits
    seat_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    template_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    documents_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Features
    features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # API access
    api_credits_included: Mapped[int] = mapped_column(Integer, default=0)
    byok_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # White-label
    custom_domain_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    custom_branding_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    image_upload_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    agencies = relationship("Agency", back_populates="plan")
