from sqlalchemy import (
    Column, Integer,
    TIMESTAMP, ForeignKey, text
)
from base import Base

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("client_profile.client_id", ondelete="RESTRICT"),
        nullable=False
    )

    status = Column(
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
