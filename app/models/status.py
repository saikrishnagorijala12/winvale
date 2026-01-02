from sqlalchemy import Column, Integer, String, TIMESTAMP
from utils.timestamp import time_now
from base import Base 


class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status_code = Column(String(10), nullable=False)

    created_time = Column(TIMESTAMP(timezone=True), default=time_now)
    updated_time = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now)
