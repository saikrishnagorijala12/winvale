from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, text, Boolean
from app.models.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone_no = Column(String(15), unique=True)
    is_active = Column(Boolean, nullable=False, default=False)
    cognito_sub = Column(String(50), unique=True, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)


    role_id = Column(
        Integer,
        ForeignKey("role.role_id", ondelete="RESTRICT"),
        nullable=False
    )

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    role = relationship("Role")