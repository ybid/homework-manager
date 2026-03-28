import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


async def get_wechat_openid(code: str):
    """通过 code 获取微信 openid"""
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "errcode" in data:
        raise Exception(f"微信登录失败: {data.get('errmsg')}")

    return {
        "openid": data.get("openid"),
        "session_key": data.get("session_key"),
        "unionid": data.get("unionid"),
    }


async def login(code: str, db: Session):
    """用户登录"""
    wx_data = await get_wechat_openid(code)
    openid = wx_data["openid"]

    user = db.query(User).filter(User.openid == openid).first()
    is_new = False

    if not user:
        user = User(
            openid=openid,
            unionid=wx_data.get("unionid"),
            nick_name=f"用户{datetime.now().strftime('%H%M%S')}",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True
        logger.info(f"新用户注册: {user.id}")

    user.last_login_at = datetime.now()
    db.commit()

    token = create_access_token({"user_id": user.id, "role": user.role})

    return {
        "token": token,
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "nick_name": user.nick_name,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "total_points": user.total_points,
        },
        "is_new": is_new,
    }


def get_user_info(user: User):
    return {
        "id": user.id,
        "nick_name": user.nick_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "total_points": user.total_points,
        "total_earned": user.total_earned,
        "total_spent": user.total_spent,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def update_user_info(user: User, data: dict, db: Session):
    if data.get("nick_name"):
        user.nick_name = data["nick_name"]
    if data.get("avatar_url"):
        user.avatar_url = data["avatar_url"]
    db.commit()
    return get_user_info(user)
