"""Template endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.template import TemplateResponse
from app.services.template_service import TemplateService
from app.services.agency_service import AgencyService

router = APIRouter()


@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """List available templates for the current agency."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    # Check if agency has pro plan
    agency = await AgencyService.get_by_id(db, current_user.agency_id)
    include_pro = agency and agency.plan_id is not None

    templates = await TemplateService.list_available(
        db=db,
        agency_id=current_user.agency_id,
        include_pro=include_pro,
    )
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get a specific template."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    template = await TemplateService.get_by_id(db, template_id)
    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Check access
    if template.is_pro:
        agency = await AgencyService.get_by_id(db, current_user.agency_id)
        if not agency or not agency.plan_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pro subscription required for this template",
            )

    return template


@router.get("/{template_id}/preview")
async def get_template_preview(
    template_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get template preview image."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    template = await TemplateService.get_by_id(db, template_id)
    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    if not template.preview_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preview not available for this template",
        )

    return RedirectResponse(url=template.preview_url)
