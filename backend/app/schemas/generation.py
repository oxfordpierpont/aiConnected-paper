"""Generation schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class GenerationRequest(BaseModel):
    """Content generation request schema."""

    topic: str
    client_id: str
    template_id: Optional[str] = None
    tone: Optional[str] = None
    keywords: Optional[List[str]] = None
    services: Optional[List[str]] = None
    custom_direction: Optional[str] = None
    auto_distribute: bool = False
    distribution_platforms: Optional[List[str]] = None


class GenerationStatus(BaseModel):
    """Generation status response schema."""

    job_id: str
    document_id: str
    status: str
    current_step: Optional[str] = None
    progress_percent: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class GenerationJobResponse(BaseModel):
    """Generation job response schema."""

    id: str
    document_id: str
    status: str
    current_step: Optional[str] = None
    progress_percent: int
    steps: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tokens_used: Optional[int] = None
    api_cost: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
