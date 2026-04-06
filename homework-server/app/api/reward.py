from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.reward import RewardInfo, ExchangeRequest
from app.services.reward_service import list_rewards, exchange_reward
from app.utils.response import success_response

router = APIRouter(prefix="/rewards", tags=["奖品"])


@router.get("")
def list_rw(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """奖品列表（只展示上架且有库存的）"""
    items = list_rewards(db, active_only=True)
    data = [RewardInfo.model_validate(r).model_dump() for r in items]
    return success_response(data=data)


@router.post("/{reward_id}/exchange")
def exchange(
    reward_id: int,
    req: ExchangeRequest = ExchangeRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """兑换奖品"""
    result = exchange_reward(db, current_user.id, reward_id, req.quantity)
    return success_response(data=result)
