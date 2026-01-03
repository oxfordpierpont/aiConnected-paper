"""Common/shared schemas."""

from typing import Generic, TypeVar, List, Optional

from pydantic import BaseModel


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination request parameters."""

    page: int = 1
    per_page: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: dict


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    message: Optional[str] = None
