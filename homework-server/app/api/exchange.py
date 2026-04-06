from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.exchange import ExchangeInfo
from app.services.reward_service import list_exchanges
from app.utils.response import paginated_response

router = APIRouter(prefix="/exchanges", tags=["兑换记录"])


@router.get("")
def list_ex(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """兑换记录"""
    items, total = list_exchanges(db, current_user.id, page, page_size)
    data = [ExchangeInfo.model_validate(ex).model_dump() for ex in items]
    return paginated_response(items=data, total=total, page=page, page_size=page_size)
