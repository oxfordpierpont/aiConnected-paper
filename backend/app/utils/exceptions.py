"""Custom exception classes."""

from typing import Any, Dict, Optional


class ContentStrategistException(Exception):
    """Base exception for Content Strategist."""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(ContentStrategistException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, code="AUTH_ERROR", **kwargs)


class AuthorizationError(ContentStrategistException):
    """Authorization/permission denied."""

    def __init__(self, message: str = "Permission denied", **kwargs):
        super().__init__(message, code="AUTHZ_ERROR", **kwargs)


class NotFoundError(ContentStrategistException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", **kwargs):
        super().__init__(f"{resource} not found", code="NOT_FOUND", **kwargs)


class ValidationError(ContentStrategistException):
    """Validation failed."""

    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)


class SeatLimitError(ContentStrategistException):
    """Agency seat limit exceeded."""

    def __init__(self, limit: int, **kwargs):
        super().__init__(
            f"Seat limit of {limit} exceeded",
            code="SEAT_LIMIT_EXCEEDED",
            details={"limit": limit},
            **kwargs,
        )


class GenerationError(ContentStrategistException):
    """Content generation failed."""

    def __init__(self, message: str = "Content generation failed", **kwargs):
        super().__init__(message, code="GENERATION_ERROR", **kwargs)


class ExternalServiceError(ContentStrategistException):
    """External service error (API, etc.)."""

    def __init__(self, service: str, message: str = "Service unavailable", **kwargs):
        super().__init__(
            f"{service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
            **kwargs,
        )
