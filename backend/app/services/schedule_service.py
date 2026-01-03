"""Schedule service."""

from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ScheduledContent, Client


class ScheduleService:
    """Service for scheduled content operations."""

    @staticmethod
    async def get_by_id(
        db: AsyncSession, schedule_id: str, agency_id: str
    ) -> Optional[ScheduledContent]:
        """Get scheduled content by ID within an agency."""
        result = await db.execute(
            select(ScheduledContent)
            .join(Client, ScheduledContent.client_id == Client.id)
            .where(ScheduledContent.id == schedule_id, Client.agency_id == agency_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_agency(
        db: AsyncSession,
        agency_id: str,
        page: int = 1,
        per_page: int = 20,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[ScheduledContent], int]:
        """List scheduled content for an agency with pagination."""
        base_conditions = [Client.agency_id == agency_id]

        if client_id:
            base_conditions.append(ScheduledContent.client_id == client_id)
        if start_date:
            base_conditions.append(ScheduledContent.scheduled_date >= start_date)
        if end_date:
            base_conditions.append(ScheduledContent.scheduled_date <= end_date)

        # Build query
        query = (
            select(ScheduledContent)
            .join(Client, ScheduledContent.client_id == Client.id)
            .where(and_(*base_conditions))
        )
        count_query = (
            select(func.count(ScheduledContent.id))
            .join(Client, ScheduledContent.client_id == Client.id)
            .where(and_(*base_conditions))
        )

        # Get total count
        total = await db.scalar(count_query)

        # Get paginated results
        query = query.order_by(ScheduledContent.scheduled_date.asc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        items = result.scalars().all()

        return list(items), total or 0

    @staticmethod
    async def create(
        db: AsyncSession,
        client_id: str,
        topic: str,
        scheduled_date: datetime,
        created_by_id: Optional[str] = None,
        **kwargs,
    ) -> ScheduledContent:
        """Create scheduled content."""
        scheduled = ScheduledContent(
            client_id=client_id,
            topic=topic,
            scheduled_date=scheduled_date,
            created_by_id=created_by_id,
            status="pending",
            **kwargs,
        )
        db.add(scheduled)
        await db.commit()
        await db.refresh(scheduled)
        return scheduled

    @staticmethod
    async def update(
        db: AsyncSession, scheduled: ScheduledContent, **kwargs
    ) -> ScheduledContent:
        """Update scheduled content."""
        for key, value in kwargs.items():
            if hasattr(scheduled, key) and value is not None:
                setattr(scheduled, key, value)
        await db.commit()
        await db.refresh(scheduled)
        return scheduled

    @staticmethod
    async def delete(db: AsyncSession, scheduled: ScheduledContent) -> None:
        """Delete scheduled content."""
        await db.delete(scheduled)
        await db.commit()

    @staticmethod
    async def get_pending_for_processing(
        db: AsyncSession, before_date: datetime
    ) -> List[ScheduledContent]:
        """Get pending scheduled content ready for processing."""
        result = await db.execute(
            select(ScheduledContent)
            .where(
                ScheduledContent.status == "pending",
                ScheduledContent.scheduled_date <= before_date,
            )
            .order_by(ScheduledContent.scheduled_date.asc())
        )
        return list(result.scalars().all())
