"""Schedule endpoints."""

from typing import Annotated
from datetime import datetime
import math
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.schedule import (
    ScheduledContentCreate,
    ScheduledContentUpdate,
    ScheduledContentResponse,
)
from app.services.schedule_service import ScheduleService
from app.services.client_service import ClientService

router = APIRouter()


@router.get("")
async def list_scheduled_content(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    client_id: str = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
):
    """List scheduled content for the current agency."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    items, total = await ScheduleService.list_by_agency(
        db=db,
        agency_id=current_user.agency_id,
        page=page,
        per_page=per_page,
        client_id=client_id,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page) if total > 0 else 0,
    }


@router.post("", response_model=ScheduledContentResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_content(
    schedule_data: ScheduledContentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Create scheduled content."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    # Verify client belongs to agency
    client = await ClientService.get_by_id(db, schedule_data.client_id, current_user.agency_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    # Create scheduled content
    scheduled = await ScheduleService.create(
        db=db,
        client_id=client.id,
        topic=schedule_data.topic,
        scheduled_date=schedule_data.scheduled_date,
        template_id=schedule_data.template_id,
        generation_options=schedule_data.generation_options,
        auto_distribute=schedule_data.auto_distribute,
        distribution_platforms=schedule_data.distribution_platforms,
        created_by_id=current_user.id,
    )

    return scheduled


@router.get("/{schedule_id}", response_model=ScheduledContentResponse)
async def get_scheduled_content(
    schedule_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Get a specific scheduled content item."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    scheduled = await ScheduleService.get_by_id(db, schedule_id, current_user.agency_id)
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled content not found",
        )
    return scheduled


@router.patch("/{schedule_id}", response_model=ScheduledContentResponse)
async def update_scheduled_content(
    schedule_id: str,
    update_data: ScheduledContentUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Update scheduled content."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    scheduled = await ScheduleService.get_by_id(db, schedule_id, current_user.agency_id)
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled content not found",
        )

    if scheduled.status not in ["pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update scheduled content with status: {scheduled.status}",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    scheduled = await ScheduleService.update(db, scheduled, **update_dict)
    return scheduled


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_content(
    schedule_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """Delete scheduled content."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    scheduled = await ScheduleService.get_by_id(db, schedule_id, current_user.agency_id)
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled content not found",
        )

    if scheduled.status not in ["pending", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete scheduled content with status: {scheduled.status}",
        )

    await ScheduleService.delete(db, scheduled)


@router.post("/import-csv")
async def import_schedule_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Import scheduled content from CSV."""
    if not current_user.agency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an agency",
        )

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    created_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            # Validate required fields
            if not row.get("client_id") or not row.get("topic") or not row.get("scheduled_date"):
                errors.append(f"Row {row_num}: Missing required fields")
                continue

            # Verify client
            client = await ClientService.get_by_id(
                db, row["client_id"], current_user.agency_id
            )
            if not client:
                errors.append(f"Row {row_num}: Client not found")
                continue

            # Parse date
            scheduled_date = datetime.fromisoformat(row["scheduled_date"])

            # Create scheduled content
            await ScheduleService.create(
                db=db,
                client_id=client.id,
                topic=row["topic"],
                scheduled_date=scheduled_date,
                template_id=row.get("template_id"),
                auto_distribute=row.get("auto_distribute", "").lower() == "true",
                created_by_id=current_user.id,
            )
            created_count += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    return {
        "message": f"Import completed. Created {created_count} scheduled items.",
        "created": created_count,
        "errors": errors,
    }


@router.get("/template/download")
async def download_csv_template(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Download CSV template for schedule import."""
    # Create CSV template
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "client_id",
        "topic",
        "scheduled_date",
        "template_id",
        "auto_distribute",
    ])
    writer.writerow([
        "example-client-uuid",
        "The Future of AI in Marketing",
        "2024-03-15T09:00:00",
        "",
        "false",
    ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=schedule_import_template.csv"},
    )
