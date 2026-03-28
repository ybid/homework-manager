from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.common import success, fail, paginate
from app.services import points_service

router = APIRouter(prefix="/points", tags=["积分管理"])


class CompleteHomeworkBody(BaseModel):
    date: Optional[str] = None
    note: Optional[str] = None


@router.post("/complete/{homework_id}")
def complete_homework(
    homework_id: int,
    body: CompleteHomeworkBody,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if body.date:
            complete_date = date.fromisoformat(body.date)
        else:
            complete_date = date.today()
        result = points_service.complete_homework(
            current_user.id, homework_id, complete_date, body.note, db
        )
        return success(result, "打卡成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
def get_points_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(points_service.get_points_stats(current_user.id, db))


@router.get("/logs")
def get_point_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs, total = points_service.get_point_logs(current_user.id, page, page_size, type, db)
    return paginate([{
        "id": log.id,
        "type": log.type,
        "amount": log.amount,
        "balance": log.balance,
        "source": log.source,
        "source_id": log.source_id,
        "description": log.description,
        "expire_at": log.expire_at.isoformat() if log.expire_at else None,
        "is_expired": log.is_expired,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    } for log in logs], total, page, page_size)
