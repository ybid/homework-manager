from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.homework import Homework, Record
from app.models.user import User


def get_weekday(d: date) -> int:
    """转换为 1-7 (周一周日)"""
    return d.isoweekday()


def should_execute_today(homework: Homework, today: date) -> bool:
    """判断作业今天是否需要执行"""
    weekday = get_weekday(today)

    if homework.type == "daily":
        return True
    elif homework.type == "weekly":
        config = homework.config or {}
        return weekday in config.get("days", [])
    elif homework.type == "monthly":
        config = homework.config or {}
        return today.day in config.get("dates", [])
    elif homework.type == "custom":
        config = homework.config or {}
        start = config.get("start_date")
        end = config.get("end_date")
        if start and end:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            return start_date <= today <= end_date
    return False


def get_homeworks(user_id: int, status: str, db: Session):
    return db.query(Homework).filter(
        Homework.user_id == user_id,
        Homework.status == status
    ).order_by(Homework.created_at.desc()).all()


def get_homework(user_id: int, homework_id: int, db: Session):
    return db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.user_id == user_id
    ).first()


def create_homework(user_id: int, data: dict, db: Session):
    # 检查名称唯一
    existing = db.query(Homework).filter(
        Homework.user_id == user_id,
        Homework.name == data["name"],
        Homework.status == "active"
    ).first()
    if existing:
        raise ValueError("作业名称已存在")

    homework = Homework(
        user_id=user_id,
        name=data["name"],
        description=data.get("description"),
        type=data["type"],
        config=data.get("config", {}),
        points=data["points"],
        penalty=data.get("penalty", 0),
        expire_days=data.get("expire_days"),
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    return homework


def update_homework(user_id: int, homework_id: int, data: dict, db: Session):
    homework = get_homework(user_id, homework_id, db)
    if not homework:
        raise ValueError("作业不存在")

    if data.get("name") and data["name"] != homework.name:
        existing = db.query(Homework).filter(
            Homework.user_id == user_id,
            Homework.name == data["name"],
            Homework.status == "active",
            Homework.id != homework_id
        ).first()
        if existing:
            raise ValueError("作业名称已存在")

    for key in ["name", "description", "config", "points", "penalty", "expire_days"]:
        if key in data and data[key] is not None:
            setattr(homework, key, data[key])

    db.commit()
    db.refresh(homework)
    return homework


def delete_homework(user_id: int, homework_id: int, db: Session):
    homework = get_homework(user_id, homework_id, db)
    if not homework:
        raise ValueError("作业不存在")
    homework.status = "archived"
    db.commit()


def get_today_homeworks(user_id: int, db: Session):
    today = date.today()

    # 获取所有活跃作业
    homeworks = db.query(Homework).filter(
        Homework.user_id == user_id,
        Homework.status == "active"
    ).all()

    # 获取今日已完成记录
    records = db.query(Record).filter(
        Record.user_id == user_id,
        Record.complete_date == today
    ).all()
    completed_ids = {r.homework_id for r in records}
    records_map = {r.homework_id: r for r in records}

    # 过滤今日应执行的作业
    today_list = []
    for hw in homeworks:
        if should_execute_today(hw, today):
            today_list.append({
                "id": hw.id,
                "name": hw.name,
                "description": hw.description,
                "type": hw.type,
                "config": hw.config,
                "points": hw.points,
                "penalty": hw.penalty,
                "completed": hw.id in completed_ids,
                "completed_at": records_map[hw.id].created_at.isoformat() if hw.id in completed_ids else None,
            })

    completed_count = sum(1 for h in today_list if h["completed"])
    today_points = sum(r.points for r in records)

    return {
        "date": today.isoformat(),
        "weekday": get_weekday(today),
        "list": today_list,
        "stats": {
            "total": len(today_list),
            "completed": completed_count,
            "pending": len(today_list) - completed_count,
            "today_points": today_points,
        }
    }


def get_calendar(user_id: int, year: int, month: int, db: Session):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)

    records = db.query(Record).filter(
        Record.user_id == user_id,
        Record.complete_date.between(start, end)
    ).order_by(Record.complete_date).all()

    calendar = {}
    for r in records:
        d = r.complete_date.isoformat()
        if d not in calendar:
            calendar[d] = {"date": d, "records": [], "total_points": 0}
        calendar[d]["records"].append({
            "id": r.id,
            "homework_id": r.homework_id,
            "homework_name": r.homework_name,
            "points": r.points,
        })
        calendar[d]["total_points"] += r.points

    return {"year": year, "month": month, "days": list(calendar.values())}
