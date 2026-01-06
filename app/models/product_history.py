from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    text
)
from app.models.base import Base

class ProductHistory(Base):
    __tablename__ = "product_history"

    product_history_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    product_id = Column(
        Integer,
        ForeignKey("product_master.product_id", ondelete="CASCADE"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("client_profiles.client_id", ondelete="RESTRICT"),
        nullable=False
    )

    item_type = Column(String(50), nullable=False)
    item_name = Column(String(50), nullable=False)
    item_description = Column(Text)

    manufacturer = Column(String(50), nullable=False)
    manufacturer_part_number = Column(String(50), nullable=False)
    client_part_number = Column(String(50))

    sin = Column(String(50))
    country_of_origin = Column(String(50))
    recycled_content_percent = Column(Numeric(5, 2))

    uom = Column(String(50))
    quantity_per_pack = Column(Integer)
    quantity_unit_uom = Column(String(50))

    nsn = Column(String(50))
    upc = Column(String(50))
    unspsc = Column(String(50))

    hazmat = Column(String(50))
    product_info_code = Column(String(50))

    url_508 = Column(Text)
    product_url = Column(Text)

    effective_start_date = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    effective_end_date = Column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
