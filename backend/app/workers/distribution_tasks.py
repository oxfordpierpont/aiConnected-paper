"""Content distribution Celery tasks."""

from celery import shared_task

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def distribute_to_linkedin(self, document_id: str, message: str = None):
    """
    Distribute document to LinkedIn.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    # TODO: Implement LinkedIn distribution
    pass


@celery_app.task(bind=True, max_retries=3)
def distribute_to_facebook(self, document_id: str, message: str = None):
    """
    Distribute document to Facebook.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    # TODO: Implement Facebook distribution
    pass


@celery_app.task(bind=True, max_retries=3)
def distribute_to_twitter(self, document_id: str, message: str = None):
    """
    Distribute document to Twitter/X.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    # TODO: Implement Twitter distribution
    pass


@celery_app.task(bind=True, max_retries=3)
def distribute_to_google_business(self, document_id: str, message: str = None):
    """
    Distribute document to Google Business Profile.

    Args:
        document_id: The document ID.
        message: Optional custom message.
    """
    # TODO: Implement Google Business distribution
    pass


@celery_app.task(bind=True)
def distribute_to_all(self, document_id: str, platforms: list, message: str = None):
    """
    Distribute document to multiple platforms.

    Args:
        document_id: The document ID.
        platforms: List of platform names.
        message: Optional custom message.
    """
    # TODO: Implement multi-platform distribution
    pass
