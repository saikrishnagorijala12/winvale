from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Text,
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

        Index(
            "ix_product_master_client",
            "client_id",
        ),

        Index(
            "ix_product_master_product_id",
            "product_id",
        ),

        Index(
            "ix_product_master_signature",
            "row_signature",
        ),
    )

    product_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
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
    commercial_list_price = Column(Numeric(5, 2))

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

    row_signature = Column(String(64), nullable=False)

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )


    #relations
    client = relationship("ClientProfile", back_populates="products")
    histories = relationship(
        "ProductHistory",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    dimension = relationship(
        "ProductDim",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan"
    )
