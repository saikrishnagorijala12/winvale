from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Numeric,
    Text,
    Date,
    TIMESTAMP,
    ForeignKey,
    text,
    Index,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class ProductMaster(Base):
    __tablename__ = "product_master"

    __table_args__ = (
        Index(
            "ux_product_master_identity",
            "client_id",
            "manufacturer",
            "manufacturer_part_number",
            unique=True,
        ),
        Index("ix_product_master_client", "client_id"),
        Index("ix_product_master_signature", "row_signature"),
    )

    product_id = Column(Integer, primary_key=True, autoincrement=True)

    client_id = Column(
        Integer,
        ForeignKey("client_profiles.client_id", ondelete="RESTRICT"),
        nullable=False,
    )

    item_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    manufacturer_part_number = Column(String(100), nullable=False)
    vendor_part_number = Column(String(100))

    sin = Column(String(50))

    item_name = Column(String(200), nullable=False)
    item_description = Column(Text)

    recycled_content_percent = Column(Numeric(5, 2))

    uom = Column(String(50))
    quantity_per_pack = Column(Integer)
    quantity_unit_uom = Column(String(50))

    currency = Column(String(3), default="USD", nullable=False)
    commercial_price = Column(Numeric(12, 2))

    mfc_name = Column(String(100))
    mfc_price = Column(Numeric(12, 2))

    govt_price_no_fee = Column(Numeric(12, 2))
    govt_price_with_fee = Column(Numeric(12, 2))

    country_of_origin = Column(String(100))

    delivery_days = Column(Integer)
    lead_time_code = Column(String(20))

    fob_us = Column(String(10))
    fob_ak = Column(String(10))
    fob_hi = Column(String(10))
    fob_pr = Column(String(10))

    nsn = Column(String(50))
    upc = Column(String(50))
    unspsc = Column(String(50))

    sale_price_with_fee = Column(Numeric(12, 2))

    start_date = Column(Date)
    stop_date = Column(Date)

    default_photo = Column(Text)
    photo_2 = Column(Text)
    photo_3 = Column(Text)
    photo_4 = Column(Text)

    product_url = Column(Text)

    warranty_period = Column(Integer)
    warranty_unit_of_time = Column(String(20))

    length = Column(Numeric(10, 2))
    width = Column(Numeric(10, 2))
    height = Column(Numeric(10, 2))

    physical_uom = Column(String(20))
    weight_lbs = Column(Numeric(10, 2))

    product_info_code = Column(String(50))
    url_508 = Column(Text)

    hazmat = Column(String(20))

    dealer_cost = Column(Numeric(12, 2))
    mfc_markup_percentage = Column(Numeric(5, 2))
    govt_markup_percentage = Column(Numeric(5, 2))
    is_deleted = Column(Boolean, default=False)

    row_signature = Column(String(64), nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    client = relationship(
        "ClientProfile",
        back_populates="products",
    )

    histories = relationship(
        "ProductHistory",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    dimension = relationship(
        "ProductDim",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    modification_actions = relationship(
        "ModificationAction",
        back_populates="product",
    )
