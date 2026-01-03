"""Generation service."""

from typing import Optional
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationJob, Document, Client


class GenerationService:
    """Service for content generation operations."""

    @staticmethod
    async def get_job_by_id(
        db: AsyncSession, job_id: str, agency_id: str
    ) -> Optional[GenerationJob]:
        """Get a generation job by ID within an agency."""
        result = await db.execute(
            select(GenerationJob)
            .join(Document, GenerationJob.document_id == Document.id)
            .where(GenerationJob.id == job_id, Document.agency_id == agency_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_job_by_document(
        db: AsyncSession, document_id: str
    ) -> Optional[GenerationJob]:
        """Get a generation job by document ID."""
        result = await db.execute(
            select(GenerationJob).where(GenerationJob.document_id == document_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_job(
        db: AsyncSession,
        document_id: str,
        celery_task_id: Optional[str] = None,
    ) -> GenerationJob:
        """Create a new generation job."""
        job = GenerationJob(
            id=str(uuid4()),
            document_id=document_id,
            status="pending",
            progress_percent=0,
            celery_task_id=celery_task_id,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def start_job(db: AsyncSession, job: GenerationJob) -> GenerationJob:
        """Mark a job as started."""
        job.status = "researching"
        job.started_at = datetime.utcnow()
        job.current_step = "topic_analysis"
        job.progress_percent = 5
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def update_progress(
        db: AsyncSession,
        job: GenerationJob,
        status: str,
        current_step: str,
        progress_percent: int,
        steps: Optional[dict] = None,
    ) -> GenerationJob:
        """Update job progress."""
        job.status = status
        job.current_step = current_step
        job.progress_percent = progress_percent
        if steps:
            job.steps = steps
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def complete_job(
        db: AsyncSession,
        job: GenerationJob,
        tokens_used: Optional[int] = None,
        api_cost: Optional[float] = None,
    ) -> GenerationJob:
        """Mark a job as completed."""
        job.status = "completed"
        job.progress_percent = 100
        job.completed_at = datetime.utcnow()
        job.current_step = None
        if tokens_used:
            job.tokens_used = tokens_used
        if api_cost:
            job.api_cost = api_cost
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def fail_job(
        db: AsyncSession,
        job: GenerationJob,
        error_message: str,
        error_code: Optional[str] = None,
    ) -> GenerationJob:
        """Mark a job as failed."""
        job.status = "failed"
        job.error_message = error_message
        job.error_code = error_code
        job.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def cancel_job(db: AsyncSession, job: GenerationJob) -> GenerationJob:
        """Cancel a running job."""
        job.status = "canceled"
        job.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def retry_job(db: AsyncSession, job: GenerationJob) -> GenerationJob:
        """Retry a failed job."""
        job.status = "pending"
        job.error_message = None
        job.error_code = None
        job.progress_percent = 0
        job.current_step = None
        job.retry_count += 1
        job.started_at = None
        job.completed_at = None
        await db.commit()
        await db.refresh(job)
        return job
