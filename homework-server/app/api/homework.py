from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.homework import (
    HomeworkCreate,
    HomeworkUpdate,
    HomeworkInfo,
    CompleteHomeworkRequest,
    RecordInfo,
    TodayHomework,
    CalendarDay,
)
from app.services.homework_service import (
    list_homeworks,
    get_homework,
    create_homework,
    update_homework,
    delete_homework,
    complete_homework,
    get_today_homeworks,
    get_calendar,
)
from app.utils.response import success_response

router = APIRouter(prefix="/homeworks", tags=["作业"])


@router.get("/today")
def today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """今日待完成作业"""
    items = get_today_homeworks(db, current_user.id)
    result = []
    for item in items:
        result.append(
            TodayHomework(
                homework=HomeworkInfo.model_validate(item["homework"]),
                completed=item["completed"],
            ).model_dump()
        )
    return success_response(data=result)


@router.get("/calendar")
def calendar(
    year: int = Query(..., ge=2000, le=2100, description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """月度日历视图"""
    items = get_calendar(db, current_user.id, year, month)
    result = []
    for item in items:
        result.append(
            CalendarDay(
                date=item["date"],
                records=[RecordInfo.model_validate(r) for r in item["records"]],
                total_points=item["total_points"],
            ).model_dump()
        )
    return success_response(data=result)


@router.get("")
def list_hw(
    status: str | None = Query(None, pattern=r"^(active|archived)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """作业列表"""
    items = list_homeworks(db, current_user.id, status)
    data = [HomeworkInfo.model_validate(hw).model_dump() for hw in items]
    return success_response(data=data)


@router.get("/{homework_id}")
def detail(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """作业详情"""
    hw = get_homework(db, homework_id, current_user.id)
    return success_response(data=HomeworkInfo.model_validate(hw).model_dump())


@router.post("")
def create(
    req: HomeworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建作业"""
    hw = create_homework(db, current_user.id, req.model_dump())
    return success_response(data=HomeworkInfo.model_validate(hw).model_dump())


@router.put("/{homework_id}")
def update(
    homework_id: int,
    req: HomeworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新作业"""
    data = req.model_dump(exclude_unset=True)
    hw = update_homework(db, homework_id, current_user.id, data)
    return success_response(data=HomeworkInfo.model_validate(hw).model_dump())


@router.delete("/{homework_id}")
def delete(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除（归档）作业"""
    delete_homework(db, homework_id, current_user.id)
    return success_response(message="作业已归档")


@router.post("/{homework_id}/complete")
def complete(
    homework_id: int,
    req: CompleteHomeworkRequest = CompleteHomeworkRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成打卡"""
    result = complete_homework(db, homework_id, current_user.id, req.note, req.complete_date)
    return success_response(data=result)
