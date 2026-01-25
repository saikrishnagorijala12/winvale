from sqlalchemy import (
    Column, Integer,
    TIMESTAMP, ForeignKey, text
)
from app.models.base import Base
from sqlalchemy.orm import relationship

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("client_profiles.client_id", ondelete="RESTRICT"),
        nullable=False
    )

    status_id = Column(
        Integer,
        ForeignKey("status.status_id", ondelete="RESTRICT"),
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

    user = relationship("User", back_populates="jobs")
    client = relationship("ClientProfile", back_populates="jobs")
    status = relationship("Status", back_populates="jobs")
    modification_actions = relationship(
        "ModificationAction",
        back_populates="job",
        cascade="all, delete-orphan"
    )
