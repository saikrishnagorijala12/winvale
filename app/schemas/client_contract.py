from datetime import datetime
from typing import Optional
from .base import ORMBase

class ClientContractCreate(ORMBase):
    client_id: int
    contract_number: str
    origin_country: Optional[str]

    gsa_proposed_discount: Optional[float]
    q_v_discount: Optional[str]
    additional_concessions: Optional[str]

    normal_delivery_time: Optional[int]
    expedited_delivery_time: Optional[int]

    fob_term: Optional[str]
    energy_star_compliance: Optional[str]

class ClientContractRead(ORMBase):
    client_profile_id: int
    client_id: int
    contract_number: str
    created_time: datetime
    updated_time: datetime

class ClientContractUpdate(ORMBase):
    origin_country: Optional[str] = None
    gsa_proposed_discount: Optional[float] = None
    q_v_discount: Optional[str] = None
    additional_concessions: Optional[str] = None
    normal_delivery_time: Optional[int] = None
    expedited_delivery_time: Optional[int] = None
    fob_term: Optional[str] = None
    energy_star_compliance: Optional[str] = None
