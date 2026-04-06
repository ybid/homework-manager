from __future__ import annotations

from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    unionid: Mapped[str | None] = mapped_column(String(64), default=None)
    nick_name: Mapped[str] = mapped_column(String(50), nullable=False, default="用户")
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    homeworks = relationship("Homework", back_populates="user", lazy="dynamic")
    records = relationship("Record", back_populates="user", lazy="dynamic")
    point_logs = relationship("PointLog", back_populates="user", lazy="dynamic")
    exchanges = relationship("Exchange", back_populates="user", lazy="dynamic")
