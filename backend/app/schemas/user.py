"""User schemas."""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    """User creation schema."""

    password: str
    role: str = "agency_member"


class UserUpdate(BaseModel):
    """User update schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """User response schema."""

    id: str
    role: str
    is_active: bool
    is_verified: bool
    agency_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
