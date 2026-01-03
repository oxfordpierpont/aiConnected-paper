"""Template service."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Template, Agency


class TemplateService:
    """Service for template operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: str) -> Optional[Template]:
        """Get a template by ID."""
        result = await db.execute(select(Template).where(Template.id == template_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Template]:
        """Get a template by slug."""
        result = await db.execute(select(Template).where(Template.slug == slug))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_available(
        db: AsyncSession,
        agency_id: str,
        include_pro: bool = False,
    ) -> List[Template]:
        """List templates available to an agency."""
        # Build conditions based on plan
        conditions = [Template.is_active == True]

        if not include_pro:
            # Only show public (free) templates if not pro
            conditions.append(Template.is_public == True)

        result = await db.execute(
            select(Template)
            .where(*conditions)
            .order_by(Template.display_order.asc(), Template.name.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all(db: AsyncSession) -> List[Template]:
        """List all active templates."""
        result = await db.execute(
            select(Template)
            .where(Template.is_active == True)
            .order_by(Template.display_order.asc(), Template.name.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        slug: str,
        template_path: str,
        **kwargs,
    ) -> Template:
        """Create a new template."""
        template = Template(
            name=name,
            slug=slug,
            template_path=template_path,
            **kwargs,
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def update(db: AsyncSession, template: Template, **kwargs) -> Template:
        """Update a template."""
        for key, value in kwargs.items():
            if hasattr(template, key) and value is not None:
                setattr(template, key, value)
        await db.commit()
        await db.refresh(template)
        return template
