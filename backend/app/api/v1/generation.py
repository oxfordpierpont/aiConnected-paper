"""Content generation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.generation import GenerationRequest, GenerationStatus, GenerationJobResponse

router = APIRouter()


@router.post("/generate", response_model=GenerationStatus, status_code=status.HTTP_202_ACCEPTED)
async def start_generation(
    request: GenerationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Start content generation for a topic."""
    # TODO: Implement generation start (creates document and job, queues task)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get generation job status."""
    # TODO: Implement job status retrieval
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Job not found",
    )


@router.post("/jobs/{job_id}/cancel")
async def cancel_generation_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running generation job."""
    # TODO: Implement job cancellation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.post("/jobs/{job_id}/retry")
async def retry_generation_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed generation job."""
    # TODO: Implement job retry
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )
