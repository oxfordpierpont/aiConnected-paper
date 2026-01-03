"""Template schemas."""

from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class TemplateBase(BaseModel):
    """Base template schema."""

    name: str
    description: Optional[str] = None


class TemplateCreate(TemplateBase):
    """Template creation schema."""

    slug: str
    template_path: str
    config: Optional[Dict[str, Any]] = None
    is_public: bool = False
    is_pro: bool = True


class TemplateUpdate(BaseModel):
    """Template update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Template response schema."""

    id: str
    slug: str
    preview_url: Optional[str] = None
    is_public: bool
    is_pro: bool
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
