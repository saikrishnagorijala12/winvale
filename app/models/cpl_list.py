from sqlalchemy import (
    Column, Integer, Text, Numeric,
    TIMESTAMP, ForeignKey, text
)
from app.models.base import Base

class CPLList(Base):
    __tablename__ = "cpl_list"

    cpl_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    client_id = Column(
        Integer,
        ForeignKey("client_profiles.client_id", ondelete="RESTRICT"),
        nullable=False
    )

    manufacturer_name = Column(Text, nullable=False)

    manufacturer_part_number = Column(Text, nullable=False)
    item_name = Column(Text, nullable=False)
    item_description = Column(Text)

    commercial_list_price = Column(Numeric(10, 2))
    origin_country = Column(Text)

    uploaded_by = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
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
