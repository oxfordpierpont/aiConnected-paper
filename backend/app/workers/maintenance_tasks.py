"""Maintenance and cleanup tasks."""

from celery import shared_task

from app.workers.celery_app import celery_app


@celery_app.task
def cleanup_expired_documents():
    """
    Clean up expired documents.

    Runs daily via Celery beat.
    - Soft-delete documents past expiry date
    - Hard-delete documents 30 days after soft-delete
    - Remove associated files from storage
    """
    # TODO: Implement document cleanup
    pass


@celery_app.task
def reset_monthly_usage():
    """
    Reset monthly usage counters.

    Runs daily, checks if new month and resets counters.
    """
    # TODO: Implement usage reset
    pass


@celery_app.task
def cleanup_temp_files():
    """
    Clean up temporary files.

    Runs daily to remove old temp files.
    """
    # TODO: Implement temp file cleanup
    pass


@celery_app.task
def send_usage_warnings():
    """
    Send usage warning emails to agencies approaching limits.

    Runs daily to check usage levels.
    """
    # TODO: Implement usage warnings
    pass
