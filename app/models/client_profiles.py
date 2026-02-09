from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base
from sqlalchemy.orm import relationship

class ClientProfile(Base):
    __tablename__ = "client_profiles"
    __table_args__ = {"schema": "dev"}

    client_id = Column(Integer, primary_key=True, autoincrement=True)

    company_name = Column(String(51), nullable=False)
    company_email = Column(String(50), nullable=False, unique=True)
    company_phone_no = Column(String(15), nullable=False, unique=True)
    company_address = Column(String(50), nullable=False)
    company_city = Column(String(50), nullable=False)
    company_state = Column(String(50), nullable=False)
    company_zip = Column(String(7), nullable=False)



    contact_officer_name = Column(String(30))
    contact_officer_email = Column(String(50), unique=True)
    contact_officer_phone_no = Column(String(15), unique=True)
    contact_officer_address = Column(String(50))
    contact_officer_city = Column(String(50))
    contact_officer_state = Column(String(50))
    contact_officer_zip = Column(String(7))


    status_id = Column(
        Integer,
        ForeignKey("dev.status.status_id", ondelete="RESTRICT"),
        nullable=False
    )
    is_deleted = Column(Boolean, nullable=False, default=False)
    # company_logo = Column(String())


    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    status = relationship(
    "Status",
    back_populates="clients",
    lazy="joined"
)
    products = relationship("ProductMaster", back_populates="client", cascade="all, delete-orphan",)
    contracts = relationship("ClientContracts", back_populates="client",uselist=False, cascade="all, delete-orphan",)
    jobs = relationship("Job", back_populates="client")
    uploads = relationship("FileUpload", back_populates="client")
    actions = relationship("ModificationAction", back_populates="client")
    cpl_items = relationship("CPLList", back_populates="client")
    product_histories = relationship(
        "ProductHistory",
        back_populates="client",
        cascade="all, delete-orphan"
    )