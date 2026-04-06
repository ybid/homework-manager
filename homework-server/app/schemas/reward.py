from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class RewardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="奖品名称")
    description: str | None = Field(None, max_length=200, description="奖品描述")
    image_url: str | None = Field(None, max_length=500, description="奖品图片URL")
    points: int = Field(..., ge=1, description="所需积分")
    stock: int = Field(..., ge=0, description="库存")


class RewardUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=200)
    image_url: str | None = Field(None, max_length=500)
    points: int | None = Field(None, ge=1)
    stock: int | None = Field(None, ge=0)
    status: str | None = Field(None, pattern=r"^(active|inactive)$")


class RewardInfo(BaseModel):
    id: int
    name: str
    description: str | None
    image_url: str | None
    points: int
    stock: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExchangeRequest(BaseModel):
    quantity: int = Field(default=1, ge=1, le=100, description="兑换数量")
