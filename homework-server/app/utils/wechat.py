from __future__ import annotations

import httpx
from app.config import get_settings
from app.utils.response import AppException

settings = get_settings()

WECHAT_LOGIN_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def code2session(code: str) -> dict:
    """Exchange WeChat login code for openid and session_key."""
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(WECHAT_LOGIN_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise AppException(
            code=10010,
            message=f"微信登录失败: {data.get('errmsg', '未知错误')}",
        )

    openid = data.get("openid")
    if not openid:
        raise AppException(code=10010, message="微信登录失败: 未获取到openid")

    return {
        "openid": openid,
        "session_key": data.get("session_key", ""),
        "unionid": data.get("unionid"),
    }
