"""Schedule schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class ScheduledContentBase(BaseModel):
    """Base scheduled content schema."""

    topic: str
    scheduled_date: datetime


class ScheduledContentCreate(ScheduledContentBase):
    """Scheduled content creation schema."""

    client_id: str
    template_id: Optional[str] = None
    generation_options: Optional[Dict[str, Any]] = None
    auto_distribute: bool = False
    distribution_platforms: Optional[List[str]] = None


class ScheduledContentUpdate(BaseModel):
    """Scheduled content update schema."""

    topic: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[str] = None


class ScheduledContentResponse(ScheduledContentBase):
    """Scheduled content response schema."""

    id: str
    status: str
    template_id: Optional[str] = None
    auto_distribute: bool
    distribution_platforms: Optional[List[str]] = None
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    client_id: str
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
