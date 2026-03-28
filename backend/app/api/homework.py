from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.homework import HomeworkCreate, HomeworkUpdate
from app.schemas.common import success, fail
from app.services import homework_service

router = APIRouter(prefix="/homeworks", tags=["作业管理"])


@router.get("/today")
def get_today_homeworks(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(homework_service.get_today_homeworks(current_user.id, db))


@router.get("/calendar")
def get_calendar(
    year: int = Query(...),
    month: int = Query(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return success(homework_service.get_calendar(current_user.id, year, month, db))


@router.get("")
def get_homeworks(
    status: str = Query("active"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    homeworks = homework_service.get_homeworks(current_user.id, status, db)
    return success([{
        "id": h.id,
        "name": h.name,
        "description": h.description,
        "type": h.type,
        "config": h.config,
        "points": h.points,
        "penalty": h.penalty,
        "expire_days": h.expire_days,
        "status": h.status,
        "created_at": h.created_at.isoformat() if h.created_at else None,
        "updated_at": h.updated_at.isoformat() if h.updated_at else None,
    } for h in homeworks])


@router.get("/{homework_id}")
def get_homework(homework_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    h = homework_service.get_homework(current_user.id, homework_id, db)
    if not h:
        raise HTTPException(status_code=404, detail="作业不存在")
    return success({
        "id": h.id,
        "name": h.name,
        "description": h.description,
        "type": h.type,
        "config": h.config,
        "points": h.points,
        "penalty": h.penalty,
        "expire_days": h.expire_days,
        "status": h.status,
        "created_at": h.created_at.isoformat() if h.created_at else None,
        "updated_at": h.updated_at.isoformat() if h.updated_at else None,
    })


@router.post("")
def create_homework(data: HomeworkCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        h = homework_service.create_homework(current_user.id, data.model_dump(), db)
        return success({
            "id": h.id,
            "name": h.name,
            "type": h.type,
            "points": h.points,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }, "创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{homework_id}")
def update_homework(homework_id: int, data: HomeworkUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        h = homework_service.update_homework(current_user.id, homework_id, data.model_dump(), db)
        return success({
            "id": h.id,
            "name": h.name,
            "type": h.type,
            "points": h.points,
            "updated_at": h.updated_at.isoformat() if h.updated_at else None,
        }, "更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{homework_id}")
def delete_homework(homework_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        homework_service.delete_homework(current_user.id, homework_id, db)
        return success(None, "删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
