from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.homework import Homework, Record, PointLog
from app.models.user import User


def complete_homework(user_id: int, homework_id: int, complete_date: date, note: str, db: Session):
    """完成打卡，获得积分"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.user_id == user_id,
        Homework.status == "active"
    ).first()

    if not homework:
        raise ValueError("作业不存在")

    # 检查是否已打卡
    existing = db.query(Record).filter(
        Record.user_id == user_id,
        Record.homework_id == homework_id,
        Record.complete_date == complete_date
    ).first()

    if existing:
        raise ValueError("今日已完成打卡")

    # 创建打卡记录
    record = Record(
        user_id=user_id,
        homework_id=homework_id,
        homework_name=homework.name,
        points=homework.points,
        complete_date=complete_date,
        note=note,
    )
    db.add(record)

    # 计算过期时间
    expire_at = None
    if homework.expire_days:
        expire_at = datetime.now() + timedelta(days=homework.expire_days)

    # 更新用户积分
    user = db.query(User).filter(User.id == user_id).first()
    new_balance = user.total_points + homework.points

    user.total_points = new_balance
    user.total_earned += homework.points

    # 创建积分流水
    log = PointLog(
        user_id=user_id,
        type="earn",
        amount=homework.points,
        balance=new_balance,
        source="homework",
        source_id=homework_id,
        description=f"完成作业: {homework.name}",
        expire_at=expire_at,
    )
    db.add(log)
    db.commit()
    db.refresh(record)

    return {
        "record_id": record.id,
        "points": homework.points,
        "total_points": new_balance,
        "complete_date": complete_date.isoformat(),
    }


def get_points_stats(user_id: int, db: Session):
    """获取积分统计"""
    user = db.query(User).filter(User.id == user_id).first()
    today = date.today()
    month_start = today.replace(day=1)

    # 今日获得
    today_logs = db.query(func.sum(PointLog.amount)).filter(
        PointLog.user_id == user_id,
        PointLog.type == "earn",
        func.date(PointLog.created_at) >= today
    ).scalar() or 0

    # 本月获得
    month_logs = db.query(func.sum(PointLog.amount)).filter(
        PointLog.user_id == user_id,
        PointLog.type == "earn",
        func.date(PointLog.created_at) >= month_start
    ).scalar() or 0

    # 即将过期 (7天内)
    expire_date = datetime.now() + timedelta(days=7)
    expiring = db.query(func.sum(PointLog.amount)).filter(
        PointLog.user_id == user_id,
        PointLog.type == "earn",
        PointLog.is_expired == False,
        PointLog.expire_at.isnot(None),
        PointLog.expire_at <= expire_date,
        PointLog.expire_at >= datetime.now()
    ).scalar() or 0

    return {
        "total_points": user.total_points,
        "today_points": today_logs,
        "month_points": month_logs,
        "total_earned": user.total_earned,
        "total_spent": user.total_spent,
        "expiring_points": expiring,
    }


def get_point_logs(user_id: int, page: int, page_size: int, log_type: str, db: Session):
    """获取积分流水"""
    query = db.query(PointLog).filter(PointLog.user_id == user_id)

    if log_type and log_type in ["earn", "spend", "expire", "adjust"]:
        query = query.filter(PointLog.type == log_type)

    total = query.count()
    logs = query.order_by(PointLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return logs, total
