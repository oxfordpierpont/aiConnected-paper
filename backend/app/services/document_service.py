"""Document service."""

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from python_slugify import slugify

from app.models import Document


class DocumentService:
    """Service for document operations."""

    @staticmethod
    async def get_by_id(
        db: AsyncSession, document_id: str, agency_id: str
    ) -> Optional[Document]:
        """Get a document by ID within an agency."""
        result = await db.execute(
            select(Document).where(
                Document.id == document_id, Document.agency_id == agency_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_agency(
        db: AsyncSession,
        agency_id: str,
        page: int = 1,
        per_page: int = 20,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Document], int]:
        """List documents for an agency with pagination."""
        query = select(Document).where(Document.agency_id == agency_id)
        count_query = select(func.count(Document.id)).where(
            Document.agency_id == agency_id
        )

        if client_id:
            query = query.where(Document.client_id == client_id)
            count_query = count_query.where(Document.client_id == client_id)

        if status:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)

        # Get total count
        total = await db.scalar(count_query)

        # Get paginated results
        query = query.order_by(Document.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        documents = result.scalars().all()

        return list(documents), total or 0

    @staticmethod
    async def create(
        db: AsyncSession,
        agency_id: str,
        client_id: str,
        title: str,
        topic: str,
        created_by_id: Optional[str] = None,
        **kwargs,
    ) -> Document:
        """Create a new document."""
        document = Document(
            agency_id=agency_id,
            client_id=client_id,
            title=title,
            topic=topic,
            slug=slugify(title),
            created_by_id=created_by_id,
            **kwargs,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def update(db: AsyncSession, document: Document, **kwargs) -> Document:
        """Update a document."""
        for key, value in kwargs.items():
            if hasattr(document, key) and value is not None:
                setattr(document, key, value)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def delete(db: AsyncSession, document: Document) -> None:
        """Delete a document."""
        await db.delete(document)
        await db.commit()
