"""Content distribution Celery tasks."""

import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Document
from app.workers.celery_app import celery_app


def get_async_session():
    """Create an async session for task context."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


async def get_document(db: AsyncSession, document_id: str) -> Optional[Document]:
    """Fetch document by ID."""
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@celery_app.task(bind=True, max_retries=3)
def distribute_to_linkedin(self, document_id: str, message: str = None):
    """
    Distribute document to LinkedIn.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    try:
        asyncio.run(_distribute_to_linkedin_async(document_id, message))
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _distribute_to_linkedin_async(document_id: str, message: str = None):
    """Async implementation of LinkedIn distribution."""
    async with get_async_session() as db:
        document = await get_document(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # In production, this would:
        # 1. Get LinkedIn OAuth credentials for the agency
        # 2. Create a post with the document link/content
        # 3. Use LinkedIn API to publish

        # For now, log the action
        print(f"[LinkedIn] Would distribute document '{document.title}' with message: {message}")

        # Update distribution log
        distribution_log = document.distribution_log or {}
        distribution_log["linkedin"] = {
            "status": "simulated",
            "distributed_at": datetime.utcnow().isoformat(),
            "message": message,
        }
        document.distribution_log = distribution_log
        await db.commit()


@celery_app.task(bind=True, max_retries=3)
def distribute_to_facebook(self, document_id: str, message: str = None):
    """
    Distribute document to Facebook.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    try:
        asyncio.run(_distribute_to_facebook_async(document_id, message))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _distribute_to_facebook_async(document_id: str, message: str = None):
    """Async implementation of Facebook distribution."""
    async with get_async_session() as db:
        document = await get_document(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        print(f"[Facebook] Would distribute document '{document.title}' with message: {message}")

        distribution_log = document.distribution_log or {}
        distribution_log["facebook"] = {
            "status": "simulated",
            "distributed_at": datetime.utcnow().isoformat(),
            "message": message,
        }
        document.distribution_log = distribution_log
        await db.commit()


@celery_app.task(bind=True, max_retries=3)
def distribute_to_twitter(self, document_id: str, message: str = None):
    """
    Distribute document to Twitter/X.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    try:
        asyncio.run(_distribute_to_twitter_async(document_id, message))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _distribute_to_twitter_async(document_id: str, message: str = None):
    """Async implementation of Twitter distribution."""
    async with get_async_session() as db:
        document = await get_document(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        print(f"[Twitter] Would distribute document '{document.title}' with message: {message}")

        distribution_log = document.distribution_log or {}
        distribution_log["twitter"] = {
            "status": "simulated",
            "distributed_at": datetime.utcnow().isoformat(),
            "message": message,
        }
        document.distribution_log = distribution_log
        await db.commit()


@celery_app.task(bind=True, max_retries=3)
def distribute_to_google_business(self, document_id: str, message: str = None):
    """
    Distribute document to Google Business Profile.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    try:
        asyncio.run(_distribute_to_google_business_async(document_id, message))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _distribute_to_google_business_async(document_id: str, message: str = None):
    """Async implementation of Google Business distribution."""
    async with get_async_session() as db:
        document = await get_document(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        print(f"[Google Business] Would distribute document '{document.title}' with message: {message}")

        distribution_log = document.distribution_log or {}
        distribution_log["google_business"] = {
            "status": "simulated",
            "distributed_at": datetime.utcnow().isoformat(),
            "message": message,
        }
        document.distribution_log = distribution_log
        await db.commit()


@celery_app.task(bind=True)
def distribute_to_all(self, document_id: str, platforms: list, message: str = None):
    """
    Distribute document to multiple platforms.

    Args:
        document_id: The document ID.
        platforms: List of platform names.
        message: Optional custom message.
    """
    platform_tasks = {
        "linkedin": distribute_to_linkedin,
        "facebook": distribute_to_facebook,
        "twitter": distribute_to_twitter,
        "google_business": distribute_to_google_business,
    }

    results = {}
    for platform in platforms:
        task_func = platform_tasks.get(platform.lower())
        if task_func:
            # Queue each platform distribution as a separate task
            task_result = task_func.delay(document_id, message)
            results[platform] = task_result.id
        else:
            results[platform] = f"Unknown platform: {platform}"

    return results
