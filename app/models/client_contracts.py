from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)
from app.models.base import Base

class ClientContracts(Base):
    __tablename__ = "client_contracts"

    client_profile_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

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
        ForeignKey("client_profiles.client_id", ondelete="RESTRICT"),
        nullable=False
    )

    client_company_logo = Column(String(50))
    signatory_name = Column(String(128))
    signatory_title = Column(String(50))

    created_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_time = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
