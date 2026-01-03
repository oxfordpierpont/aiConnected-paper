"""Celery application configuration."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "content_strategist",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.generation_tasks",
        "app.workers.distribution_tasks",
        "app.workers.scheduled_tasks",
        "app.workers.maintenance_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "process-scheduled-content": {
        "task": "app.workers.scheduled_tasks.process_scheduled_content",
        "schedule": 300.0,  # Every 5 minutes
    },
    "cleanup-expired-documents": {
        "task": "app.workers.maintenance_tasks.cleanup_expired_documents",
        "schedule": 86400.0,  # Daily
    },
    "reset-monthly-usage": {
        "task": "app.workers.maintenance_tasks.reset_monthly_usage",
        "schedule": 86400.0,  # Daily (checks if month changed)
    },
}
