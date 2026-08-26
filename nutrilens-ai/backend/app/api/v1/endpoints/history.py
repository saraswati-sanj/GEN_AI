"""
NutriLens AI — User Scan History API Endpoints
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.scan_history import ScanHistory
from app.models.schemas import PaginatedHistory, ScanHistoryItem, ScanHistoryDetail
from app.models.user import User
from app.api.v1.endpoints.users import get_current_user

router = APIRouter(prefix="/history", tags=["Scan History"])


@router.get("/", response_model=PaginatedHistory)
async def list_scan_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated scan history for the current user."""
    offset = (page - 1) * page_size

    # Total count query
    count_query = select(func.count()).select_from(ScanHistory).where(ScanHistory.user_id == current_user.id)
    total_res = await db.execute(count_query)
    total = total_res.scalar_one() or 0

    # Data query
    data_query = (
        select(ScanHistory)
        .where(ScanHistory.user_id == current_user.id)
        .order_by(ScanHistory.scanned_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items_res = await db.execute(data_query)
    scans = items_res.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedHistory(
        items=[ScanHistoryItem.model_validate(s) for s in scans],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{scan_id}", response_model=ScanHistoryDetail)
async def get_scan_detail(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get complete details and full AI analysis for a past scan."""
    query = select(ScanHistory).where(
        ScanHistory.id == scan_id,
        ScanHistory.user_id == current_user.id
    )
    res = await db.execute(query)
    scan = res.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found.",
        )
    return ScanHistoryDetail.model_validate(scan)


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single scan record from history."""
    query = select(ScanHistory).where(
        ScanHistory.id == scan_id,
        ScanHistory.user_id == current_user.id
    )
    res = await db.execute(query)
    scan = res.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found.",
        )
    await db.delete(scan)
    await db.commit()
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all scan history records for the current user."""
    stmt = delete(ScanHistory).where(ScanHistory.user_id == current_user.id)
    await db.execute(stmt)
    await db.commit()
    return None
