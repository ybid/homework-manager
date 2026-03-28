from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.schemas.reward import RewardCreate, RewardUpdate, ExchangeRequest
from app.schemas.common import success, fail, paginate
from app.services import reward_service

router = APIRouter(prefix="/rewards", tags=["奖品管理"])


@router.get("")
def get_rewards(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(reward_service.get_rewards("active", db))


@router.post("/{reward_id}/exchange")
def exchange_reward(
    reward_id: int,
    data: ExchangeRequest = ExchangeRequest(),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = reward_service.exchange_reward(current_user.id, reward_id, data.quantity, db)
        return success(result, "兑换成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/exchanges")
def get_exchanges(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exchanges, total = reward_service.get_exchanges(current_user.id, page, page_size, db)
    return paginate([{
        "id": e.id,
        "reward_name": e.reward_name,
        "reward_image": e.reward_image,
        "points": e.points,
        "quantity": e.quantity,
        "status": e.status,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    } for e in exchanges], total, page, page_size)


# 管理员接口
admin_router = APIRouter(prefix="/admin", tags=["管理员"])


@admin_router.post("/rewards")
def create_reward(data: RewardCreate, current_user=Depends(get_admin_user), db: Session = Depends(get_db)):
    reward = reward_service.create_reward(current_user.id, data.model_dump(), db)
    return success({
        "id": reward.id,
        "name": reward.name,
        "points": reward.points,
        "stock": reward.stock,
        "status": reward.status,
        "created_at": reward.created_at.isoformat() if reward.created_at else None,
    }, "创建成功")


@admin_router.put("/rewards/{reward_id}")
def update_reward(reward_id: int, data: RewardUpdate, current_user=Depends(get_admin_user), db: Session = Depends(get_db)):
    try:
        reward = reward_service.update_reward(reward_id, data.model_dump(), db)
        return success({
            "id": reward.id,
            "name": reward.name,
            "points": reward.points,
            "stock": reward.stock,
            "updated_at": reward.updated_at.isoformat() if reward.updated_at else None,
        }, "更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@admin_router.delete("/rewards/{reward_id}")
def delete_reward(reward_id: int, current_user=Depends(get_admin_user), db: Session = Depends(get_db)):
    try:
        reward_service.delete_reward(reward_id, db)
        return success(None, "删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
