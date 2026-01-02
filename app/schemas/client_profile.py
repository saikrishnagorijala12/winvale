from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClientProfileBase(BaseModel):
    contract_number: str
    origin_country: Optional[str] = None

    gsa_proposed_discount: Optional[float] = None
    q_v_discount: Optional[str] = None
    additional_concessions: Optional[str] = None

    normal_delivery_time: Optional[int] = None
    expedited_delivery_time: Optional[int] = None

    fob_term: Optional[str] = None
    energy_star_compliance: Optional[str] = None

    vendor_id: int

    client_company_logo: Optional[str] = None
    signatory_name: Optional[str] = None
    signatory_title: Optional[str] = None


class ClientProfileCreate(ClientProfileBase):
    pass


class ClientProfileRead(ClientProfileBase):
    vendor_profile_id: int
    created_time: datetime
    updated_time: datetime

    class Config:
        orm_mode = True
