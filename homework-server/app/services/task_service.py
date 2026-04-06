from __future__ import annotations

import logging
from datetime import datetime, date, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import SessionLocal
from app.models.point_log import PointLog
from app.models.homework import Homework
from app.models.record import Record
from app.models.user import User

logger = logging.getLogger(__name__)


def expire_points():
    """Expire points that have passed their expire_at datetime. Runs daily at 00:05."""
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        # Find unexpired earn logs that have passed expire_at
        expired_logs = db.query(PointLog).filter(
            PointLog.type == "earn",
            PointLog.is_expired == False,
            PointLog.expire_at != None,
            PointLog.expire_at <= now,
        ).all()

        for log in expired_logs:
            log.is_expired = True

            # Deduct points from user
            user = db.query(User).filter(User.id == log.user_id).with_for_update().first()
            if not user:
                continue

            deduct = min(log.amount, user.total_points)
            if deduct <= 0:
                continue

            user.total_points -= deduct
            new_balance = user.total_points

            expire_log = PointLog(
                user_id=user.id,
                type="expire",
                amount=-deduct,
                balance=new_balance,
                source="expire",
                source_id=log.id,
                description=f"积分过期 (来源记录ID: {log.id})",
            )
            db.add(expire_log)

        db.commit()
        logger.info(f"Expired {len(expired_logs)} point logs")
    except Exception as e:
        db.rollback()
        logger.error(f"Error expiring points: {e}")
    finally:
        db.close()


def penalize_incomplete():
    """Penalize users for incomplete daily homeworks. Runs daily at 23:55."""
    db: Session = SessionLocal()
    try:
        today = date.today()

        # Get all active daily homeworks with penalty > 0
        homeworks = db.query(Homework).filter(
            Homework.status == "active",
            Homework.type == "daily",
            Homework.penalty > 0,
        ).all()

        penalized_count = 0
        for hw in homeworks:
            # Check if user completed this homework today
            record = db.query(Record).filter(
                Record.user_id == hw.user_id,
                Record.homework_id == hw.id,
                Record.complete_date == today,
            ).first()

            if record:
                continue  # Completed, skip

            # Apply penalty
            user = db.query(User).filter(User.id == hw.user_id).with_for_update().first()
            if not user:
                continue

            deduct = min(hw.penalty, user.total_points)
            if deduct <= 0:
                continue

            user.total_points -= deduct
            user.total_spent += deduct
            new_balance = user.total_points

            penalty_log = PointLog(
                user_id=user.id,
                type="spend",
                amount=-deduct,
                balance=new_balance,
                source="homework",
                source_id=hw.id,
                description=f"未完成作业惩罚: {hw.name}",
            )
            db.add(penalty_log)
            penalized_count += 1

        db.commit()
        logger.info(f"Penalized {penalized_count} incomplete homeworks")
    except Exception as e:
        db.rollback()
        logger.error(f"Error penalizing incomplete homeworks: {e}")
    finally:
        db.close()
