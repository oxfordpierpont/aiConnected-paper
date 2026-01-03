"""Maintenance and cleanup tasks."""

import asyncio
import os
import shutil
from datetime import datetime, timedelta

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Document, Agency
from app.workers.celery_app import celery_app


def get_async_session():
    """Create an async session for task context."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


@celery_app.task
def cleanup_expired_documents():
    """
    Clean up expired documents.

    Runs daily via Celery beat.
    - Soft-delete documents past expiry date
    - Hard-delete documents 30 days after soft-delete
    - Remove associated files from storage
    """
    asyncio.run(_cleanup_expired_documents_async())


async def _cleanup_expired_documents_async():
    """Async implementation of document cleanup."""
    async with get_async_session() as db:
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)

            # Hard-delete documents that were soft-deleted more than 30 days ago
            stmt = select(Document).where(
                Document.deleted_at.isnot(None),
                Document.deleted_at < thirty_days_ago,
            ).limit(50)

            result = await db.execute(stmt)
            docs_to_delete = result.scalars().all()

            for doc in docs_to_delete:
                # Remove PDF file if exists
                if doc.pdf_path and os.path.exists(doc.pdf_path):
                    try:
                        os.remove(doc.pdf_path)
                    except OSError:
                        pass

                # Hard delete
                await db.delete(doc)

            await db.commit()

            # Soft-delete documents past expiry (if expiry feature is enabled)
            # Note: expiry_date field would need to be added to model if needed

        except Exception as e:
            print(f"Error cleaning up documents: {e}")


@celery_app.task
def reset_monthly_usage():
    """
    Reset monthly usage counters.

    Runs daily, checks if new month and resets counters.
    """
    asyncio.run(_reset_monthly_usage_async())


async def _reset_monthly_usage_async():
    """Async implementation of usage reset."""
    async with get_async_session() as db:
        try:
            now = datetime.utcnow()

            # Check if it's the first day of the month (or first run of the month)
            if now.day != 1:
                # Could also check last_reset_date on agency
                return

            # Reset usage counters for all agencies
            stmt = update(Agency).values(
                current_month_generations=0,
                last_usage_reset=now,
            )
            await db.execute(stmt)
            await db.commit()

            print(f"Reset monthly usage for all agencies at {now}")

        except Exception as e:
            print(f"Error resetting monthly usage: {e}")


@celery_app.task
def cleanup_temp_files():
    """
    Clean up temporary files.

    Runs daily to remove old temp files.
    """
    try:
        temp_dir = os.path.join(settings.STORAGE_LOCAL_PATH, "temp")

        if not os.path.exists(temp_dir):
            return

        now = datetime.now()
        max_age_hours = 24  # Remove files older than 24 hours

        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)

            try:
                # Check file age
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_hours = (now - mtime).total_seconds() / 3600

                if age_hours > max_age_hours:
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
            except OSError:
                continue

        print(f"Cleaned up temp files older than {max_age_hours} hours")

    except Exception as e:
        print(f"Error cleaning up temp files: {e}")


@celery_app.task
def send_usage_warnings():
    """
    Send usage warning emails to agencies approaching limits.

    Runs daily to check usage levels.
    """
    asyncio.run(_send_usage_warnings_async())


async def _send_usage_warnings_async():
    """Async implementation of usage warnings."""
    async with get_async_session() as db:
        try:
            # Find agencies at 80% or more of their monthly limit
            from app.models import Plan

            stmt = select(Agency).join(Plan).where(
                Agency.current_month_generations >= Plan.monthly_generations * 0.8,
                Agency.usage_warning_sent.is_(None),
            )

            result = await db.execute(stmt)
            agencies = result.scalars().all()

            for agency in agencies:
                # In production, send email notification
                # For now, just log and mark as warned
                print(f"Usage warning: Agency {agency.name} is at {agency.current_month_generations} generations")

                # Mark as warned (would send email in production)
                agency.usage_warning_sent = datetime.utcnow()
                await db.commit()

        except Exception as e:
            print(f"Error sending usage warnings: {e}")
