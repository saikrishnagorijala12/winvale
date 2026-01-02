from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)
from sqlalchemy.dialects.postgresql import JSONB
from base import Base

class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    company_name = Column(String(30), nullable=False)
    company_email = Column(String(50), nullable=False, unique=True)
    company_phone_no = Column(String(15), nullable=False, unique=True)
    company_address = Column(JSONB, nullable=False)

    contact_officer_name = Column(String(30), nullable=False)
    contact_officer_email = Column(String(50), nullable=False, unique=True)
    contact_officer_phone_no = Column(String(15), nullable=False, unique=True)
    contact_officer_address = Column(JSONB, nullable=False)

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
