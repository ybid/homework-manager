from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Date, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    type = Column(String(20), nullable=False)  # daily/weekly/monthly/custom
    config = Column(JSON, nullable=True)
    points = Column(Integer, nullable=False)
    penalty = Column(Integer, default=0)
    expire_days = Column(Integer, nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Record(Base):
    __tablename__ = "records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    homework_id = Column(BigInteger, nullable=False, index=True)
    homework_name = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    complete_date = Column(Date, nullable=False)
    note = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class PointLog(Base):
    __tablename__ = "point_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    type = Column(String(20), nullable=False)  # earn/spend/expire/adjust
    amount = Column(Integer, nullable=False)
    balance = Column(Integer, nullable=False)
    source = Column(String(20), nullable=False)  # homework/exchange/expire/adjust
    source_id = Column(BigInteger, nullable=True)
    description = Column(String(200), nullable=True)
    expire_at = Column(DateTime, nullable=True)
    is_expired = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
