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
from app.models.base import Base
from sqlalchemy.orm import relationship

class ClientContracts(Base):
    __tablename__ = "client_contracts"

    client_profile_id = Column(
        Integer, primary_key=True, autoincrement=True
    )

    contract_officer_name = Column(String(30))
    contract_officer_address = Column(String(50))
    contract_officer_city = Column(String(50))
    contract_officer_state = Column(String(50))
    contract_officer_zip = Column(String(7))


    contract_number = Column(String(50), nullable=False)
    origin_country = Column(String(50))
    

    gsa_proposed_discount = Column(Numeric(5, 2))
    q_v_discount = Column(String(50))
    additional_concessions = Column(String(50))

    normal_delivery_time = Column(Integer)
    expedited_delivery_time = Column(Integer)

    fob_term = Column(String(50))
    energy_star_compliance = Column(String(50))

    client_id = Column(
        Integer,
        ForeignKey("client_profiles.client_id",  ondelete="RESTRICT"),
        nullable=False,  unique=True
    )

    client_company_logo = Column(String(50))
    signatory_name = Column(String(128))
    signatory_title = Column(String(50))
    is_deleted = Column(Boolean, nullable=False, default=False)


    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    client = relationship(
        "ClientProfile",
        back_populates="contracts"
    )
