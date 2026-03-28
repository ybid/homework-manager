from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.reward import Reward, Exchange
from app.models.homework import PointLog
from app.models.user import User


def get_rewards(status: str, db: Session):
    """获取奖品列表"""
    rewards = db.query(Reward).filter(Reward.status == status).order_by(Reward.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "image_url": r.image_url,
            "points": r.points,
            "stock": r.stock,
            "status": r.status,
            "sold_out": r.stock <= 0,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rewards
    ]


def create_reward(admin_id: int, data: dict, db: Session):
    """创建奖品"""
    reward = Reward(
        name=data["name"],
        description=data.get("description"),
        image_url=data.get("image_url"),
        points=data["points"],
        stock=data["stock"],
        status=data.get("status", "active"),
        created_by=admin_id,
    )
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward


def update_reward(reward_id: int, data: dict, db: Session):
    """更新奖品"""
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise ValueError("奖品不存在")

    for key in ["name", "description", "image_url", "points", "stock", "status"]:
        if key in data and data[key] is not None:
            setattr(reward, key, data[key])

    db.commit()
    db.refresh(reward)
    return reward


def delete_reward(reward_id: int, db: Session):
    """删除奖品（下架）"""
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise ValueError("奖品不存在")
    reward.status = "inactive"
    db.commit()


def exchange_reward(user_id: int, reward_id: int, quantity: int, db: Session):
    """兑换奖品"""
    reward = db.query(Reward).filter(Reward.id == reward_id, Reward.status == "active").first()

    if not reward:
        raise ValueError("奖品不存在或已下架")
    if reward.stock < quantity:
        raise ValueError("库存不足")

    user = db.query(User).filter(User.id == user_id).first()
    points_needed = reward.points * quantity

    if user.total_points < points_needed:
        raise ValueError(f"积分不足，还需 {points_needed - user.total_points} 积分")

    # 扣减库存
    reward.stock -= quantity

    # 创建兑换记录
    exchange = Exchange(
        user_id=user_id,
        reward_id=reward_id,
        reward_name=reward.name,
        reward_image=reward.image_url,
        points=points_needed,
        quantity=quantity,
    )
    db.add(exchange)

    # 更新用户积分
    new_balance = user.total_points - points_needed
    user.total_points = new_balance
    user.total_spent += points_needed

    # 创建积分流水
    log = PointLog(
        user_id=user_id,
        type="spend",
        amount=-points_needed,
        balance=new_balance,
        source="exchange",
        source_id=exchange.id,
        description=f"兑换奖品: {reward.name}",
    )
    db.add(log)
    db.commit()
    db.refresh(exchange)

    return {
        "exchange_id": exchange.id,
        "reward_name": reward.name,
        "points": points_needed,
        "remaining_points": new_balance,
        "created_at": exchange.created_at.isoformat(),
    }


def get_exchanges(user_id: int, page: int, page_size: int, db: Session):
    """获取兑换记录"""
    query = db.query(Exchange).filter(Exchange.user_id == user_id)
    total = query.count()
    exchanges = query.order_by(Exchange.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return exchanges, total
