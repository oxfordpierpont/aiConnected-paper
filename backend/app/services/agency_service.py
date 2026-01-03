"""Agency service."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.models import Agency


class AgencyService:
    """Service for agency operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, agency_id: str) -> Optional[Agency]:
        """Get an agency by ID."""
        result = await db.execute(select(Agency).where(Agency.id == agency_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_subdomain(db: AsyncSession, subdomain: str) -> Optional[Agency]:
        """Get an agency by subdomain."""
        result = await db.execute(select(Agency).where(Agency.subdomain == subdomain))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_custom_domain(db: AsyncSession, domain: str) -> Optional[Agency]:
        """Get an agency by custom domain."""
        result = await db.execute(select(Agency).where(Agency.custom_domain == domain))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, name: str, subdomain: str, **kwargs) -> Agency:
        """Create a new agency."""
        agency = Agency(
            name=name,
            subdomain=subdomain,
            slug=slugify(name),
            **kwargs,
        )
        db.add(agency)
        await db.commit()
        await db.refresh(agency)
        return agency

    @staticmethod
    async def update(db: AsyncSession, agency: Agency, **kwargs) -> Agency:
        """Update an agency."""
        for key, value in kwargs.items():
            if hasattr(agency, key) and value is not None:
                setattr(agency, key, value)
        await db.commit()
        await db.refresh(agency)
        return agency
