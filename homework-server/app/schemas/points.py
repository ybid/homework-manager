from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class PointStats(BaseModel):
    total_points: int
    today_earned: int
    month_earned: int
    total_earned: int
    total_spent: int
    expiring_soon: int  # 7天内即将过期的积分


class PointLogInfo(BaseModel):
    id: int
    user_id: int
    type: str
    amount: int
    balance: int
    source: str
    source_id: int | None
    description: str | None
    expire_at: datetime | None
    is_expired: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdjustPointsRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    amount: int = Field(..., description="调整积分数量（正数增加，负数减少）")
    description: str = Field(..., min_length=1, max_length=200, description="调整原因")
