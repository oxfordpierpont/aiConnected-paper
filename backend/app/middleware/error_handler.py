"""Global error handling middleware."""

import traceback
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.exceptions import ContentStrategistException


async def error_handler_middleware(request: Request, call_next: Callable):
    """Handle exceptions globally."""
    try:
        return await call_next(request)
    except ContentStrategistException as e:
        return JSONResponse(
            status_code=_get_status_code(e.code),
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                }
            },
        )
    except Exception as e:
        # Log the error
        traceback.print_exc()

        # Return generic error
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred",
                    "details": {},
                }
            },
        )


def _get_status_code(error_code: str) -> int:
    """Map error code to HTTP status code."""
    status_map = {
        "AUTH_ERROR": 401,
        "AUTHZ_ERROR": 403,
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 400,
        "SEAT_LIMIT_EXCEEDED": 403,
        "GENERATION_ERROR": 500,
        "EXTERNAL_SERVICE_ERROR": 502,
    }
    return status_map.get(error_code, 500)
