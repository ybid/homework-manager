from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserInfo, UpdateUserRequest
from app.services.user_service import get_user_info, update_user_info
from app.utils.response import success_response

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/info")
def info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    data = get_user_info(current_user)
    return success_response(data=UserInfo(**data).model_dump())


@router.put("/info")
def update_info(
    req: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户信息"""
    user = update_user_info(db, current_user, req.nick_name, req.avatar_url)
    data = get_user_info(user)
    return success_response(data=UserInfo(**data).model_dump())
