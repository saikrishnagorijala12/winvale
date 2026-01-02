from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from base import Base 


class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status_code = Column(String(10), nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
