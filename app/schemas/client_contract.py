from datetime import datetime
from typing import Optional
from .base import ORMBase

class ClientContractCreate(ORMBase):
    contract_number: str
    contract_officer_name: Optional[str] = None
    contract_officer_address: Optional[str] = None
    contract_officer_city: Optional[str] = None
    contract_officer_state: Optional[str] = None
    contract_officer_zip: Optional[str] = None
    origin_country: Optional[str]
    is_deleted: Optional[bool] = False


    gsa_proposed_discount: Optional[float]= None
    q_v_discount: Optional[str]= None
    additional_concessions: Optional[str]= None

    normal_delivery_time: Optional[int]= None
    expedited_delivery_time: Optional[int]= None

    fob_term: Optional[str]= None
    energy_star_compliance: Optional[str]= None

class ClientContractRead(ORMBase):
    client_profile_id: int
    client_id: int
    contract_officer_name: Optional[str] = None
    contract_officer_address: Optional[str] = None
    contract_officer_city: Optional[str] = None
    contract_officer_state: Optional[str] = None
    contract_officer_zip: Optional[str] = None
    contract_number: str
    is_deleted: bool

    created_time: datetime
    updated_time: datetime

class ClientContractUpdate(ORMBase):
    contract_number: Optional[str]
    contract_officer_name: Optional[str] = None
    contract_officer_address: Optional[str] = None
    contract_officer_city: Optional[str] = None
    contract_officer_state: Optional[str] = None
    contract_officer_zip: Optional[str] = None
    origin_country: Optional[str] = None
    gsa_proposed_discount: Optional[float] = None
    q_v_discount: Optional[str] = None
    additional_concessions: Optional[str] = None
    normal_delivery_time: Optional[int] = None
    expedited_delivery_time: Optional[int] = None
    fob_term: Optional[str] = None
    energy_star_compliance: Optional[str] = None
    is_deleted: Optional[bool] = False

