from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class ExchangeInfo(BaseModel):
    id: int
    user_id: int
    reward_id: int
    reward_name: str
    reward_image: str | None
    points: int
    quantity: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
