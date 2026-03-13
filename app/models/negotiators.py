from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    text
)
from app.models.base import Base
from sqlalchemy.orm import relationship

class Negotiator(Base):
    __tablename__ = "negotiators"
    __table_args__ = {"schema": "dev"}

    negotiator_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(
        Integer,
        ForeignKey("dev.client_profiles.client_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(50), nullable=False)
    title = Column(String(50), nullable=False)
    email = Column(String(100))
    phone_no = Column(String(20))
    address = Column(String(100))
    city = Column(String(50))
    state = Column(String(50))
    zip = Column(String(7))

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    client = relationship("ClientProfile", back_populates="negotiators")
