from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True, nullable=False, index=True)
    unionid = Column(String(64), nullable=True)
    nick_name = Column(String(50), default="用户")
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default="user", index=True)
    total_points = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    status = Column(String(20), default="active")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
