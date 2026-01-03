"""Rate limiting middleware."""

import time
from typing import Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter middleware."""

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = {}
        self.limit = settings.RATE_LIMIT_REQUESTS
        self.window = settings.RATE_LIMIT_WINDOW

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        allowed, remaining, reset_at = self._check_rate_limit(client_id)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests",
                        "details": {"reset_at": reset_at},
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(int(reset_at - time.time())),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use user ID if authenticated, otherwise IP
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"

        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host}" if request.client else "ip:unknown"

    def _check_rate_limit(self, client_id: str) -> Tuple[bool, int, int]:
        """
        Check if client is within rate limit.

        Returns:
            Tuple of (allowed, remaining, reset_at)
        """
        now = time.time()
        window_start = now - self.window

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                ts for ts in self.requests[client_id] if ts > window_start
            ]
        else:
            self.requests[client_id] = []

        # Check limit
        current_count = len(self.requests[client_id])
        if current_count >= self.limit:
            oldest = min(self.requests[client_id]) if self.requests[client_id] else now
            reset_at = int(oldest + self.window)
            return False, 0, reset_at

        # Record request
        self.requests[client_id].append(now)
        remaining = self.limit - current_count - 1
        reset_at = int(now + self.window)

        return True, remaining, reset_at
