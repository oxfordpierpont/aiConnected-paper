"""Document endpoints."""

from typing import Annotated
import math

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
from app.schemas.document import DocumentResponse, DocumentUpdate

router = APIRouter()
storage_service = StorageService()


@router.get("")
async def list_documents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    client_id: str = Query(None),
    doc_status: str = Query(None, alias="status"),
):
    """List all documents for the current agency."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    documents, total = await DocumentService.list_by_agency(
        db=db,
        agency_id=current_user.agency_id,
        page=page,
        per_page=per_page,
        client_id=client_id,
        status=doc_status,
    )

    return {
        "items": documents,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page) if total > 0 else 0,
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    document = await DocumentService.get_by_id(db, document_id, current_user.agency_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Update a document."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    document = await DocumentService.get_by_id(db, document_id, current_user.agency_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    document = await DocumentService.update(db, document, **update_dict)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Delete a document."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    document = await DocumentService.get_by_id(db, document_id, current_user.agency_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await DocumentService.delete(db, document)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Download document PDF."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    document = await DocumentService.get_by_id(db, document_id, current_user.agency_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if not document.pdf_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not available for this document",
        )

    # Get file from storage
    pdf_content = await storage_service.get_file(document.pdf_url)
    if not pdf_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found",
        )

    filename = f"{document.slug}.pdf"
    return StreamingResponse(
        iter([pdf_content]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
