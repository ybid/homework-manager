from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.wechat import code2session
from app.utils.security import create_access_token


async def login_by_code(db: Session, code: str) -> dict:
    """WeChat login: exchange code for openid, find or create user, return JWT."""
    wx_data = await code2session(code)
    openid = wx_data["openid"]
    unionid = wx_data.get("unionid")

    user = db.query(User).filter(User.openid == openid).first()
    is_new = False

    if user is None:
        user = User(openid=openid, unionid=unionid)
        db.add(user)
        db.flush()
        is_new = True
    else:
        if unionid and not user.unionid:
            user.unionid = unionid

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {"token": token, "user_id": user.id, "is_new": is_new}


def get_user_info(user: User) -> dict:
    return {
        "id": user.id,
        "nick_name": user.nick_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "total_points": user.total_points,
        "total_earned": user.total_earned,
        "total_spent": user.total_spent,
        "status": user.status,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
    }


def update_user_info(db: Session, user: User, nick_name: str | None, avatar_url: str | None) -> User:
    if nick_name is not None:
        user.nick_name = nick_name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user
