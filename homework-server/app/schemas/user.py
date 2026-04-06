from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=200, description="微信登录code")


class LoginResponse(BaseModel):
    token: str
    user_id: int
    is_new: bool


class UserInfo(BaseModel):
    id: int
    nick_name: str
    avatar_url: str | None
    role: str
    total_points: int
    total_earned: int
    total_spent: int
    status: str
    last_login_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    nick_name: str | None = Field(None, min_length=1, max_length=50, description="昵称")
    avatar_url: str | None = Field(None, max_length=500, description="头像URL")


class AdminUserInfo(UserInfo):
    openid: str
    unionid: str | None
    updated_at: datetime

    class Config:
        from_attributes = True
