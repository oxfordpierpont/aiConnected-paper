"""Content generation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.generation import GenerationRequest, GenerationStatus, GenerationJobResponse
from app.services.client_service import ClientService
from app.services.document_service import DocumentService
from app.services.generation_service import GenerationService

router = APIRouter()


@router.post("/generate", response_model=GenerationStatus, status_code=status.HTTP_202_ACCEPTED)
async def start_generation(
    request: GenerationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Start content generation for a topic."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    # Verify client belongs to agency
    client = await ClientService.get_by_id(db, request.client_id, current_user.agency_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    # Create document
    document = await DocumentService.create(
        db=db,
        agency_id=current_user.agency_id,
        client_id=client.id,
        title=request.topic[:200],
        topic=request.topic,
        template_id=request.template_id,
        created_by_id=current_user.id,
        status="generating",
        generation_options={
            "tone": request.tone,
            "keywords": request.keywords,
            "services": request.services,
            "custom_direction": request.custom_direction,
            "auto_distribute": request.auto_distribute,
            "distribution_platforms": request.distribution_platforms,
        },
    )

    # Create generation job
    job = await GenerationService.create_job(db, document.id)

    # Queue the Celery task (import here to avoid circular imports)
    from app.workers.generation_tasks import generate_content_task

    celery_task = generate_content_task.delay(job.id)

    # Update job with celery task id
    job.celery_task_id = celery_task.id
    await db.commit()

    return GenerationStatus(
        job_id=job.id,
        document_id=document.id,
        status=job.status,
        current_step=job.current_step,
        progress_percent=job.progress_percent,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
    )


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get generation job status."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    job = await GenerationService.get_job_by_id(db, job_id, current_user.agency_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.post("/jobs/{job_id}/cancel")
async def cancel_generation_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running generation job."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    job = await GenerationService.get_job_by_id(db, job_id, current_user.agency_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.status in ["completed", "failed", "canceled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status}",
        )

    # Cancel Celery task if running
    if job.celery_task_id:
        from app.workers.celery_app import celery_app

        celery_app.control.revoke(job.celery_task_id, terminate=True)

    job = await GenerationService.cancel_job(db, job)

    return {"message": "Job canceled successfully", "job_id": job.id}


@router.post("/jobs/{job_id}/retry")
async def retry_generation_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed generation job."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    job = await GenerationService.get_job_by_id(db, job_id, current_user.agency_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed jobs",
        )

    if job.retry_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum retry attempts reached",
        )

    # Reset job for retry
    job = await GenerationService.retry_job(db, job)

    # Queue new Celery task
    from app.workers.generation_tasks import generate_content_task

    celery_task = generate_content_task.delay(job.id)

    job.celery_task_id = celery_task.id
    await db.commit()

    return {"message": "Job retry started", "job_id": job.id}
