"""Client schemas."""

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


class ClientBase(BaseModel):
    """Base client schema."""

    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ClientCreate(ClientBase):
    """Client creation schema."""

    services: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    tone: str = "professional"


class ClientUpdate(BaseModel):
    """Client update schema."""

    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    services: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    tone: Optional[str] = None


class ClientResponse(ClientBase):
    """Client response schema."""

    id: str
    slug: str
    logo_url: Optional[str] = None
    services: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    tone: str
    is_active: bool
    agency_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
