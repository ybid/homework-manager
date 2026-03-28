from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 奖品相关
class RewardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    description: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = None
    points: int = Field(..., ge=1)
    stock: int = Field(..., ge=0)
    status: str = Field("active", pattern="^(active|inactive)$")


class RewardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    points: Optional[int] = Field(None, ge=1)
    stock: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None


class RewardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    points: int
    stock: int
    status: str
    sold_out: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# 兑换相关
class ExchangeRequest(BaseModel):
    quantity: int = Field(1, ge=1)


class ExchangeResponse(BaseModel):
    exchange_id: int
    reward_name: str
    points: int
    remaining_points: int
    created_at: datetime


class ExchangeRecord(BaseModel):
    id: int
    reward_name: str
    reward_image: Optional[str]
    points: int
    quantity: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
