"""Agency endpoints."""

from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models import User, Agency, Client, Document, ScheduledContent
from app.services.agency_service import AgencyService
from app.schemas.agency import AgencyResponse, AgencyUpdate

router = APIRouter()


@router.get("/me", response_model=AgencyResponse)
async def get_current_agency(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get current user's agency."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    agency = await AgencyService.get_by_id(db, current_user.agency_id)
    if not agency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency not found",
        )
    return agency


@router.patch("/me", response_model=AgencyResponse)
async def update_current_agency(
    update_data: AgencyUpdate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: AsyncSession = Depends(get_db),
):
    """Update current user's agency."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    agency = await AgencyService.get_by_id(db, current_user.agency_id)
    if not agency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency not found",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    agency = await AgencyService.update(db, agency, **update_dict)
    return agency


@router.get("/me/stats")
async def get_agency_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get agency statistics."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    agency_id = current_user.agency_id

    # Get total clients
    total_clients = await db.scalar(
        select(func.count(Client.id)).where(Client.agency_id == agency_id)
    )

    # Get total documents
    total_documents = await db.scalar(
        select(func.count(Document.id)).where(Document.agency_id == agency_id)
    )

    # Get documents this month
    first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    documents_this_month = await db.scalar(
        select(func.count(Document.id)).where(
            Document.agency_id == agency_id,
            Document.created_at >= first_of_month,
        )
    )

    # Get pending scheduled content
    scheduled_content = await db.scalar(
        select(func.count(ScheduledContent.id))
        .join(Client, ScheduledContent.client_id == Client.id)
        .where(
            Client.agency_id == agency_id,
            ScheduledContent.status == "pending",
        )
    )

    return {
        "total_clients": total_clients or 0,
        "total_documents": total_documents or 0,
        "documents_this_month": documents_this_month or 0,
        "scheduled_content": scheduled_content or 0,
    }
