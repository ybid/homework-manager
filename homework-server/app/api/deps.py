from __future__ import annotations

from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import decode_access_token
from app.utils.response import AuthException, ForbiddenException


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
) -> User:
    if not authorization.startswith("Bearer "):
        raise AuthException("无效的认证格式，需要 Bearer token")

    token = authorization[7:]
    payload = decode_access_token(token)
    if payload is None:
        raise AuthException("token无效或已过期")

    user_id = payload.get("userId")
    if user_id is None:
        raise AuthException("token无效")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AuthException("用户不存在")

    if user.status == "banned":
        raise ForbiddenException("账号已被封禁")

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise ForbiddenException("需要管理员权限")
    return current_user
