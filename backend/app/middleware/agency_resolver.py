"""Agency resolver middleware for white-label domain routing."""

from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class AgencyResolverMiddleware(BaseHTTPMiddleware):
    """Middleware to resolve agency from request domain."""

    async def dispatch(self, request: Request, call_next):
        """Resolve agency from subdomain or custom domain."""
        # Extract host from request
        host = request.headers.get("host", "").split(":")[0].lower()

        # Resolve agency
        agency_info = await self._resolve_agency(host)

        # Store in request state
        request.state.agency_id = agency_info.get("id") if agency_info else None
        request.state.agency_subdomain = agency_info.get("subdomain") if agency_info else None

        response = await call_next(request)
        return response

    async def _resolve_agency(self, host: str) -> Optional[dict]:
        """
        Resolve agency from host.

        Args:
            host: The request host.

        Returns:
            Agency info dict or None.
        """
        # TODO: Implement agency resolution
        # 1. Check if it's a custom domain
        # 2. Extract subdomain from host
        # 3. Query database for matching agency
        return None
