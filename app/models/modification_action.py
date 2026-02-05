from sqlalchemy import (
    Column, Integer, Numeric, Text,
    TIMESTAMP, ForeignKey, text
)
from app.models.base import Base
from sqlalchemy.orm import relationship


class ModificationAction(Base):
    __tablename__ = "modification_action"

    action_id = Column(Integer, primary_key=True, autoincrement=True)

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

    job_id = Column(
        Integer,
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    cpl_id = Column(
        Integer,
        ForeignKey("cpl_list.cpl_id", ondelete="SET NULL"),
        nullable=True
    )

    product_id = Column(
        Integer,
        ForeignKey("product_master.product_id", ondelete="SET NULL"),
        nullable=True
    )

    action_type = Column(Text, nullable=False)

    old_price = Column(Numeric(10, 2))
    new_price = Column(Numeric(10, 2))

    old_description = Column(Text)
    new_description = Column(Text)

    old_name = Column(Text)
    new_name = Column(Text)

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


    user = relationship("User", back_populates="actions")
    client = relationship("ClientProfile", back_populates="actions")
    job = relationship(
        "Job",
        back_populates="modification_actions"
    )
    product = relationship("ProductMaster", back_populates="modification_actions")
    cpl_item = relationship("CPLList", back_populates="modification_actions")

