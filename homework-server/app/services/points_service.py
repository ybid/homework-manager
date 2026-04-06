from __future__ import annotations

from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.point_log import PointLog
from app.models.user import User
from app.utils.response import NotFoundException, BusinessException


def get_point_stats(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("用户不存在")

    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    month_start = datetime(today.year, today.month, 1)

    # Today earned
    today_earned = db.query(func.coalesce(func.sum(PointLog.amount), 0)).filter(
        PointLog.user_id == user_id,
        PointLog.type == "earn",
        PointLog.created_at >= today_start,
    ).scalar()

    # Month earned
    month_earned = db.query(func.coalesce(func.sum(PointLog.amount), 0)).filter(
        PointLog.user_id == user_id,
        PointLog.type == "earn",
        PointLog.created_at >= month_start,
    ).scalar()

    # Expiring soon (within 7 days)
    seven_days = datetime.now(timezone.utc) + timedelta(days=7)
    expiring_soon = db.query(func.coalesce(func.sum(PointLog.amount), 0)).filter(
        PointLog.user_id == user_id,
        PointLog.type == "earn",
        PointLog.is_expired == False,
        PointLog.expire_at != None,
        PointLog.expire_at <= seven_days,
    ).scalar()

    return {
        "total_points": user.total_points,
        "today_earned": int(today_earned),
        "month_earned": int(month_earned),
        "total_earned": user.total_earned,
        "total_spent": user.total_spent,
        "expiring_soon": int(expiring_soon),
    }


def get_point_logs(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    log_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[list[PointLog], int]:
    query = db.query(PointLog).filter(PointLog.user_id == user_id)

    if log_type:
        query = query.filter(PointLog.type == log_type)
    if start_date:
        query = query.filter(PointLog.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(PointLog.created_at <= datetime.combine(end_date, datetime.max.time()))

    total = query.count()
    items = query.order_by(PointLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return items, total


def adjust_points(db: Session, admin_user_id: int, target_user_id: int, amount: int, description: str) -> dict:
    """Admin adjusts user points."""
    user = db.query(User).filter(User.id == target_user_id).with_for_update().first()
    if not user:
        raise NotFoundException("目标用户不存在")

    new_balance = user.total_points + amount
    if new_balance < 0:
        raise BusinessException(code=20010, message="调整后积分不能为负数")

    user.total_points = new_balance
    if amount > 0:
        user.total_earned += amount
    else:
        user.total_spent += abs(amount)

    point_log = PointLog(
        user_id=target_user_id,
        type="adjust",
        amount=amount,
        balance=new_balance,
        source="adjust",
        source_id=admin_user_id,
        description=description,
    )
    db.add(point_log)
    db.commit()

    return {
        "user_id": target_user_id,
        "amount": amount,
        "new_balance": new_balance,
    }
