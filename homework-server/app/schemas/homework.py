from __future__ import annotations

from datetime import datetime, date
from typing import Any
from pydantic import BaseModel, Field


class HomeworkCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="作业名称")
    description: str | None = Field(None, max_length=200, description="作业描述")
    type: str = Field(..., pattern=r"^(daily|weekly|monthly|custom)$", description="类型")
    config: dict[str, Any] | None = Field(None, description="类型配置")
    points: int = Field(..., ge=1, description="完成获得积分")
    penalty: int = Field(default=0, ge=0, description="未完成惩罚积分")
    expire_days: int | None = Field(None, ge=1, description="积分过期天数")


class HomeworkUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=200)
    type: str | None = Field(None, pattern=r"^(daily|weekly|monthly|custom)$")
    config: dict[str, Any] | None = None
    points: int | None = Field(None, ge=1)
    penalty: int | None = Field(None, ge=0)
    expire_days: int | None = Field(None, ge=1)
    status: str | None = Field(None, pattern=r"^(active|archived)$")


class HomeworkInfo(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    type: str
    config: dict[str, Any] | None
    points: int
    penalty: int
    expire_days: int | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompleteHomeworkRequest(BaseModel):
    note: str | None = Field(None, max_length=200, description="打卡备注")
    complete_date: date | None = Field(None, description="完成日期（默认今天）")


class RecordInfo(BaseModel):
    id: int
    user_id: int
    homework_id: int
    homework_name: str
    points: int
    complete_date: date
    note: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TodayHomework(BaseModel):
    homework: HomeworkInfo
    completed: bool


class CalendarDay(BaseModel):
    date: date
    records: list[RecordInfo]
    total_points: int
