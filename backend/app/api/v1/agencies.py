"""Agency endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models import User
from app.schemas.agency import AgencyResponse, AgencyUpdate

router = APIRouter()


@router.get("/me", response_model=AgencyResponse)
async def get_current_agency(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get current user's agency."""
    # TODO: Implement agency retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.patch("/me", response_model=AgencyResponse)
async def update_current_agency(
    update_data: AgencyUpdate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: AsyncSession = Depends(get_db),
):
    """Update current user's agency."""
    # TODO: Implement agency update
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.get("/me/stats")
async def get_agency_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get agency statistics."""
    # TODO: Implement stats retrieval
    return {
        "total_clients": 0,
        "total_documents": 0,
        "documents_this_month": 0,
        "scheduled_content": 0,
    }
