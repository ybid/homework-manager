from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date, datetime


# 作业相关
class HomeworkCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=100)
    type: str = Field(..., pattern="^(daily|weekly|monthly|custom)$")
    config: Optional[dict] = {}
    points: int = Field(..., ge=1, le=1000)
    penalty: int = Field(0, ge=0, le=500)
    expire_days: Optional[int] = Field(None, ge=1)


class HomeworkUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    config: Optional[dict] = None
    points: Optional[int] = Field(None, ge=1, le=1000)
    penalty: Optional[int] = Field(None, ge=0, le=500)
    expire_days: Optional[int] = None


class HomeworkResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    type: str
    config: Optional[dict]
    points: int
    penalty: int
    expire_days: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class CompleteResponse(BaseModel):
    record_id: int
    points: int
    total_points: int
    complete_date: str


# 积分相关
class PointsStats(BaseModel):
    total_points: int
    today_points: int
    month_points: int
    total_earned: int
    total_spent: int
    expiring_points: int


class PointLogResponse(BaseModel):
    id: int
    type: str
    amount: int
    balance: int
    source: str
    source_id: Optional[int]
    description: Optional[str]
    expire_at: Optional[datetime]
    is_expired: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 日历相关
class CalendarDay(BaseModel):
    date: str
    records: List[dict]
    total_points: int
