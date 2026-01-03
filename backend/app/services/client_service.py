"""Client service."""

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.models import Client


class ClientService:
    """Service for client operations."""

    @staticmethod
    async def get_by_id(
        db: AsyncSession, client_id: str, agency_id: str
    ) -> Optional[Client]:
        """Get a client by ID within an agency."""
        result = await db.execute(
            select(Client).where(Client.id == client_id, Client.agency_id == agency_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_agency(
        db: AsyncSession,
        agency_id: str,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[Client], int]:
        """List clients for an agency with pagination."""
        query = select(Client).where(Client.agency_id == agency_id)
        count_query = select(func.count(Client.id)).where(Client.agency_id == agency_id)

        if search:
            query = query.where(Client.name.ilike(f"%{search}%"))
            count_query = count_query.where(Client.name.ilike(f"%{search}%"))

        # Get total count
        total = await db.scalar(count_query)

        # Get paginated results
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        clients = result.scalars().all()

        return list(clients), total or 0

    @staticmethod
    async def create(
        db: AsyncSession, agency_id: str, name: str, **kwargs
    ) -> Client:
        """Create a new client."""
        client = Client(
            agency_id=agency_id,
            name=name,
            slug=slugify(name),
            **kwargs,
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
        return client

    @staticmethod
    async def update(db: AsyncSession, client: Client, **kwargs) -> Client:
        """Update a client."""
        for key, value in kwargs.items():
            if hasattr(client, key) and value is not None:
                setattr(client, key, value)
        await db.commit()
        await db.refresh(client)
        return client

    @staticmethod
    async def delete(db: AsyncSession, client: Client) -> None:
        """Delete a client."""
        await db.delete(client)
        await db.commit()
