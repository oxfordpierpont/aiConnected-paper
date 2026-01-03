"""Agency schemas."""

from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class AgencyBase(BaseModel):
    """Base agency schema."""

    name: str
    website: Optional[str] = None


class AgencyCreate(AgencyBase):
    """Agency creation schema."""

    subdomain: str


class AgencyUpdate(BaseModel):
    """Agency update schema."""

    name: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class AgencyResponse(AgencyBase):
    """Agency response schema."""

    id: str
    slug: str
    subdomain: str
    custom_domain: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    is_active: bool
    plan_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
