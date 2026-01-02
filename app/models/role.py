from sqlalchemy import Column, Integer, String, TIMESTAMP
from utils.timestamp import time_now
from base import Base 


class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(10), nullable=False)

    created_time = Column(TIMESTAMP(timezone=True), default=time_now)
    updated_time = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now)
