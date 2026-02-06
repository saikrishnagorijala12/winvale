from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.models.base import Base 


class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"schema": "dev"}

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(10), nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    users = relationship(
        "User",
        back_populates="role",
    )
