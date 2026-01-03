"""Template endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.template import TemplateResponse

router = APIRouter()


@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """List available templates for the current agency."""
    # TODO: Implement template listing (filtered by plan access)
    return []


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get a specific template."""
    # TODO: Implement template retrieval
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Template not found",
    )


@router.get("/{template_id}/preview")
async def get_template_preview(
    template_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get template preview image."""
    # TODO: Implement template preview
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )
