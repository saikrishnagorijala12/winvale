from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from app.models.base import Base 
from sqlalchemy.orm import relationship


class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(10), nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    jobs = relationship("Job", back_populates="status")
    clients = relationship(
        "ClientProfile",
        back_populates="status"
    )