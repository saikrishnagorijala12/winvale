from sqlalchemy import (
    Column, Integer, Numeric, Text,
    TIMESTAMP, ForeignKey, text
)
from base import Base

class ModificationAction(Base):
    __tablename__ = "modification_action"

    action_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

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

    job_id = Column(
        Integer,
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    action_type = Column(Text, nullable=False)

    old_price = Column(Numeric(10, 2))
    new_price = Column(Numeric(10, 2))

    old_description = Column(Text)
    new_description = Column(Text)

    number_of_items_impacted = Column(Integer, nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
