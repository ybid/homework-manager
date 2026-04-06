from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.points import PointStats, PointLogInfo
from app.services.points_service import get_point_stats, get_point_logs
from app.utils.response import success_response, paginated_response

router = APIRouter(prefix="/points", tags=["积分"])


@router.get("/stats")
def stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """积分统计"""
    data = get_point_stats(db, current_user.id)
    return success_response(data=PointStats(**data).model_dump())


@router.get("/logs")
def logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, pattern=r"^(earn|spend|expire|adjust)$", alias="type"),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """积分流水（分页）"""
    items, total = get_point_logs(db, current_user.id, page, page_size, type, start_date, end_date)
    data = [PointLogInfo.model_validate(log).model_dump() for log in items]
    return paginated_response(items=data, total=total, page=page, page_size=page_size)
