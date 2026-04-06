from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import BigInteger, String, Integer, DateTime, Date, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Record(Base):
    __tablename__ = "records"
    __table_args__ = (
        UniqueConstraint("user_id", "homework_id", "complete_date", name="uq_user_homework_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    homework_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("homeworks.id"), nullable=False, index=True)
    homework_name: Mapped[str] = mapped_column(String(50), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    complete_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(String(200), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="records")
    homework = relationship("Homework", back_populates="records")
