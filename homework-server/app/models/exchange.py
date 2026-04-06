from __future__ import annotations

from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    reward_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rewards.id"), nullable=False, index=True)
    reward_name: Mapped[str] = mapped_column(String(50), nullable=False)
    reward_image: Mapped[str | None] = mapped_column(String(500), default=None)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="exchanges")
    reward = relationship("Reward", back_populates="exchanges")
