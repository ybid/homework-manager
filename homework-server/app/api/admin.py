from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.models.record import Record
from app.models.exchange import Exchange
from app.models.point_log import PointLog
from app.schemas.user import AdminUserInfo
from app.schemas.reward import RewardCreate, RewardUpdate, RewardInfo
from app.schemas.points import AdjustPointsRequest
from app.services.reward_service import create_reward, update_reward, delete_reward, list_rewards
from app.services.points_service import adjust_points
from app.utils.response import success_response, paginated_response

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.post("/rewards")
def admin_create_reward(
    req: RewardCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """创建奖品"""
    reward = create_reward(db, admin.id, req.model_dump())
    return success_response(data=RewardInfo.model_validate(reward).model_dump())


@router.put("/rewards/{reward_id}")
def admin_update_reward(
    reward_id: int,
    req: RewardUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """更新奖品"""
    data = req.model_dump(exclude_unset=True)
    reward = update_reward(db, reward_id, data)
    return success_response(data=RewardInfo.model_validate(reward).model_dump())


@router.delete("/rewards/{reward_id}")
def admin_delete_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """删除（下架）奖品"""
    delete_reward(db, reward_id)
    return success_response(message="奖品已下架")


@router.post("/points/adjust")
def admin_adjust_points(
    req: AdjustPointsRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """调整用户积分"""
    result = adjust_points(db, admin.id, req.user_id, req.amount, req.description)
    return success_response(data=result)


@router.get("/users")
def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, pattern=r"^(active|banned)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """用户列表"""
    query = db.query(User)
    if status:
        query = query.filter(User.status == status)
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    data = [AdminUserInfo.model_validate(u).model_dump() for u in users]
    return paginated_response(items=data, total=total, page=page, page_size=page_size)


@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """统计数据"""
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar()
    total_records = db.query(func.count(Record.id)).scalar()
    total_exchanges = db.query(func.count(Exchange.id)).scalar()
    total_points_earned = db.query(func.coalesce(func.sum(User.total_earned), 0)).scalar()
    total_points_spent = db.query(func.coalesce(func.sum(User.total_spent), 0)).scalar()

    return success_response(data={
        "total_users": total_users,
        "active_users": active_users,
        "total_records": total_records,
        "total_exchanges": total_exchanges,
        "total_points_earned": int(total_points_earned),
        "total_points_spent": int(total_points_spent),
    })
