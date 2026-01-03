"""Document schemas."""

from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class DocumentBase(BaseModel):
    """Base document schema."""

    title: str
    topic: str


class DocumentCreate(DocumentBase):
    """Document creation schema."""

    client_id: str
    template_id: Optional[str] = None
    generation_options: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """Document update schema."""

    title: Optional[str] = None
    status: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Document response schema."""

    id: str
    slug: str
    status: str
    pdf_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    statistics_count: Optional[int] = None
    sources_count: Optional[int] = None
    template_id: Optional[str] = None
    agency_id: str
    client_id: str
    created_by_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
