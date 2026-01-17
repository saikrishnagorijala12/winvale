from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)
from sqlalchemy.orm import relationship
from app.models.base import Base

class ProductDim(Base):
    __tablename__ = "product_dim"

    dim_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    product_id = Column(
        Integer,
        ForeignKey("product_master.product_id", ondelete="CASCADE"),
        nullable=False
    )

    length = Column(Numeric(10, 2))
    width = Column(Numeric(10, 2))
    height = Column(Numeric(10, 2))

    physical_uom = Column(String(50))

    weight_lbs = Column(Numeric(10, 2))
    warranty_period = Column(Integer)

    photo_type = Column(String(50))
    photo_path = Column(String(50))

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    product = relationship(
        "ProductMaster",
        back_populates="dimension",
    )
