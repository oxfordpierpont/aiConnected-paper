"""Template model."""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Template(BaseModel):
    """Template model for PDF designs."""

    __tablename__ = "templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Template files
    template_path: Mapped[str] = mapped_column(String(255), nullable=False)

    # Configuration
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Access control
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pro: Mapped[bool] = mapped_column(Boolean, default=True)

    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
