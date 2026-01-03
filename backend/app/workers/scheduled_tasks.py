"""Scheduled content processing tasks."""

import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import ScheduledContent, Document
from app.workers.celery_app import celery_app
from app.workers.generation_tasks import generate_content_task


def get_async_session():
    """Create an async session for task context."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


@celery_app.task
def process_scheduled_content():
    """
    Process scheduled content that is due for generation.

    Runs every 5 minutes via Celery beat.
    """
    asyncio.run(_process_scheduled_content_async())


async def _process_scheduled_content_async():
    """Async implementation of scheduled content processing."""
    async with get_async_session() as db:
        try:
            # Query for pending scheduled content where scheduled_date <= now
            now = datetime.utcnow()
            stmt = select(ScheduledContent).where(
                ScheduledContent.status == "pending",
                ScheduledContent.scheduled_date <= now,
            ).limit(10)  # Process 10 at a time

            result = await db.execute(stmt)
            scheduled_items = result.scalars().all()

            for item in scheduled_items:
                try:
                    # Update status to processing
                    item.status = "processing"
                    await db.commit()

                    # Create document for generation
                    document = Document(
                        agency_id=item.agency_id,
                        client_id=item.client_id,
                        title=item.topic[:200],
                        topic=item.topic,
                        template_id=item.template_id,
                        created_by_id=item.created_by_id,
                        status="generating",
                        generation_options={
                            "tone": item.generation_config.get("tone", "professional"),
                            "keywords": item.generation_config.get("keywords", []),
                            "auto_distribute": item.auto_distribute,
                            "distribution_platforms": item.distribution_platforms or [],
                        },
                    )
                    db.add(document)
                    await db.commit()
                    await db.refresh(document)

                    # Update scheduled item with document reference
                    item.document_id = document.id
                    await db.commit()

                    # Queue generation task
                    generate_content_task.delay(str(document.id))

                    # Update status to completed (generation is queued)
                    item.status = "completed"
                    await db.commit()

                except Exception as e:
                    # Mark as failed
                    item.status = "failed"
                    item.error_message = str(e)
                    await db.commit()

        except Exception as e:
            # Log error but don't raise to prevent task failure
            print(f"Error processing scheduled content: {e}")


@celery_app.task
def process_auto_distribution():
    """
    Process auto-distribution for completed documents.

    Runs after content generation completes.
    """
    asyncio.run(_process_auto_distribution_async())


async def _process_auto_distribution_async():
    """Async implementation of auto-distribution processing."""
    from app.workers.distribution_tasks import distribute_to_all

    async with get_async_session() as db:
        try:
            # Find documents that need distribution
            stmt = select(Document).where(
                Document.status == "completed",
                Document.distributed_at.is_(None),
            ).limit(10)

            result = await db.execute(stmt)
            documents = result.scalars().all()

            for doc in documents:
                options = doc.generation_options or {}
                if options.get("auto_distribute"):
                    platforms = options.get("distribution_platforms", [])
                    if platforms:
                        # Queue distribution task
                        distribute_to_all.delay(
                            str(doc.id),
                            platforms,
                            message=None,
                        )
                        # Mark as distribution queued
                        doc.distributed_at = datetime.utcnow()
                        await db.commit()

        except Exception as e:
            print(f"Error processing auto-distribution: {e}")
