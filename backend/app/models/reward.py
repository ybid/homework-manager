from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    image_url = Column(String(500), nullable=True)
    points = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    status = Column(String(20), default="active")
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    reward_id = Column(BigInteger, nullable=False, index=True)
    reward_name = Column(String(50), nullable=False)
    reward_image = Column(String(500), nullable=True)
    points = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, server_default=func.now())
