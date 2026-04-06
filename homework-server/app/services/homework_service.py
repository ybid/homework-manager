from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from calendar import monthrange
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.homework import Homework
from app.models.record import Record
from app.models.point_log import PointLog
from app.models.user import User
from app.utils.response import NotFoundException, BusinessException, ValidationException


def list_homeworks(db: Session, user_id: int, status: str | None = None) -> list[Homework]:
    query = db.query(Homework).filter(Homework.user_id == user_id)
    if status:
        query = query.filter(Homework.status == status)
    return query.order_by(Homework.created_at.desc()).all()


def get_homework(db: Session, homework_id: int, user_id: int) -> Homework:
    hw = db.query(Homework).filter(Homework.id == homework_id, Homework.user_id == user_id).first()
    if not hw:
        raise NotFoundException("作业不存在")
    return hw


def create_homework(db: Session, user_id: int, data: dict) -> Homework:
    hw = Homework(user_id=user_id, **data)
    db.add(hw)
    db.commit()
    db.refresh(hw)
    return hw


def update_homework(db: Session, homework_id: int, user_id: int, data: dict) -> Homework:
    hw = get_homework(db, homework_id, user_id)
    for key, value in data.items():
        if value is not None:
            setattr(hw, key, value)
    db.commit()
    db.refresh(hw)
    return hw


def delete_homework(db: Session, homework_id: int, user_id: int) -> None:
    hw = get_homework(db, homework_id, user_id)
    hw.status = "archived"
    db.commit()


def complete_homework(
    db: Session, homework_id: int, user_id: int, note: str | None = None, complete_date: date | None = None
) -> dict:
    """Complete a homework (transactional: record + point_log + user points)."""
    if complete_date is None:
        complete_date = date.today()

    # 1. Get homework and validate ownership
    hw = get_homework(db, homework_id, user_id)
    if hw.status != "active":
        raise BusinessException(code=20001, message="该作业已归档，无法打卡")

    # 2. Check duplicate (unique constraint will also catch this)
    existing = db.query(Record).filter(
        Record.user_id == user_id,
        Record.homework_id == homework_id,
        Record.complete_date == complete_date,
    ).first()
    if existing:
        raise BusinessException(code=20002, message="今日已完成该作业，不可重复打卡")

    # 3. Create record
    record = Record(
        user_id=user_id,
        homework_id=homework_id,
        homework_name=hw.name,
        points=hw.points,
        complete_date=complete_date,
        note=note,
    )
    db.add(record)
    db.flush()

    # 4. Update user points
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        raise NotFoundException("用户不存在")
    user.total_points += hw.points
    user.total_earned += hw.points
    new_balance = user.total_points

    # 5. Create point log
    expire_at = None
    if hw.expire_days:
        expire_at = datetime.now(timezone.utc) + timedelta(days=hw.expire_days)

    point_log = PointLog(
        user_id=user_id,
        type="earn",
        amount=hw.points,
        balance=new_balance,
        source="homework",
        source_id=record.id,
        description=f"完成作业: {hw.name}",
        expire_at=expire_at,
    )
    db.add(point_log)

    db.commit()
    db.refresh(record)

    return {
        "record_id": record.id,
        "points_earned": hw.points,
        "total_points": new_balance,
    }


def get_today_homeworks(db: Session, user_id: int) -> list[dict]:
    """Get today's homeworks with completion status."""
    today = date.today()
    homeworks = db.query(Homework).filter(
        Homework.user_id == user_id,
        Homework.status == "active",
    ).all()

    today_records = db.query(Record).filter(
        Record.user_id == user_id,
        Record.complete_date == today,
    ).all()
    completed_hw_ids = {r.homework_id for r in today_records}

    result = []
    for hw in homeworks:
        # Filter based on homework type
        should_show = False
        if hw.type == "daily":
            should_show = True
        elif hw.type == "weekly":
            # Show on configured days or all days if no config
            if hw.config and "days" in hw.config:
                should_show = today.isoweekday() in hw.config["days"]
            else:
                should_show = True
        elif hw.type == "monthly":
            if hw.config and "days" in hw.config:
                should_show = today.day in hw.config["days"]
            else:
                should_show = True
        elif hw.type == "custom":
            should_show = True

        if should_show:
            result.append({
                "homework": hw,
                "completed": hw.id in completed_hw_ids,
            })

    return result


def get_calendar(db: Session, user_id: int, year: int, month: int) -> list[dict]:
    """Get monthly calendar view with records."""
    if not (1 <= month <= 12):
        raise ValidationException("月份必须在1-12之间")
    if not (2000 <= year <= 2100):
        raise ValidationException("年份必须在2000-2100之间")

    _, days_in_month = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, days_in_month)

    records = db.query(Record).filter(
        Record.user_id == user_id,
        Record.complete_date >= start_date,
        Record.complete_date <= end_date,
    ).order_by(Record.complete_date).all()

    # Group records by date
    from collections import defaultdict
    date_records: dict[date, list] = defaultdict(list)
    for r in records:
        date_records[r.complete_date].append(r)

    calendar_data = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        day_records = date_records.get(d, [])
        calendar_data.append({
            "date": d,
            "records": day_records,
            "total_points": sum(r.points for r in day_records),
        })

    return calendar_data
