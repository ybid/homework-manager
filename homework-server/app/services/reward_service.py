from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models.reward import Reward
from app.models.exchange import Exchange
from app.models.point_log import PointLog
from app.models.user import User
from app.utils.response import NotFoundException, BusinessException


def list_rewards(db: Session, active_only: bool = True) -> list[Reward]:
    query = db.query(Reward)
    if active_only:
        query = query.filter(Reward.status == "active", Reward.stock > 0)
    return query.order_by(Reward.created_at.desc()).all()


def get_reward(db: Session, reward_id: int) -> Reward:
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise NotFoundException("奖品不存在")
    return reward


def create_reward(db: Session, admin_id: int, data: dict) -> Reward:
    reward = Reward(created_by=admin_id, **data)
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward


def update_reward(db: Session, reward_id: int, data: dict) -> Reward:
    reward = get_reward(db, reward_id)
    for key, value in data.items():
        if value is not None:
            setattr(reward, key, value)
    db.commit()
    db.refresh(reward)
    return reward


def delete_reward(db: Session, reward_id: int) -> None:
    reward = get_reward(db, reward_id)
    reward.status = "inactive"
    db.commit()


def exchange_reward(db: Session, user_id: int, reward_id: int, quantity: int = 1) -> dict:
    """Exchange reward (transactional with optimistic lock on stock)."""
    # 1. Get reward and validate
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise NotFoundException("奖品不存在")
    if reward.status != "active":
        raise BusinessException(code=20020, message="该奖品已下架")
    if reward.stock < quantity:
        raise BusinessException(code=20021, message="奖品库存不足")

    total_cost = reward.points * quantity

    # 2. Check user points
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        raise NotFoundException("用户不存在")
    if user.total_points < total_cost:
        raise BusinessException(code=20022, message="积分不足")

    # 3. Deduct stock with optimistic lock
    result = db.execute(
        update(Reward)
        .where(Reward.id == reward_id, Reward.stock >= quantity)
        .values(stock=Reward.stock - quantity)
    )
    if result.rowcount == 0:
        raise BusinessException(code=20021, message="奖品库存不足")

    # 4. Create exchange record
    exchange = Exchange(
        user_id=user_id,
        reward_id=reward_id,
        reward_name=reward.name,
        reward_image=reward.image_url,
        points=total_cost,
        quantity=quantity,
    )
    db.add(exchange)
    db.flush()

    # 5. Deduct user points
    user.total_points -= total_cost
    user.total_spent += total_cost
    new_balance = user.total_points

    # 6. Create point log
    point_log = PointLog(
        user_id=user_id,
        type="spend",
        amount=-total_cost,
        balance=new_balance,
        source="exchange",
        source_id=exchange.id,
        description=f"兑换奖品: {reward.name} x{quantity}",
    )
    db.add(point_log)

    db.commit()

    return {
        "exchange_id": exchange.id,
        "points_spent": total_cost,
        "total_points": new_balance,
    }


def list_exchanges(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> tuple[list[Exchange], int]:
    query = db.query(Exchange).filter(Exchange.user_id == user_id)
    total = query.count()
    items = query.order_by(Exchange.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total
