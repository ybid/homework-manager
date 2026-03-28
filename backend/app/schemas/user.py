from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 用户相关
class UserLogin(BaseModel):
    code: str


class UserLoginResponse(BaseModel):
    token: str
    expires_in: int
    user: dict
    is_new: bool


class UserInfo(BaseModel):
    id: int
    nick_name: str
    avatar_url: Optional[str] = None
    role: str
    total_points: int
    total_earned: int
    total_spent: int


class UserUpdate(BaseModel):
    nick_name: Optional[str] = None
    avatar_url: Optional[str] = None
