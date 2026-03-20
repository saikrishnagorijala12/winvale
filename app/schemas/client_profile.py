from datetime import datetime
from typing import Optional
from pydantic import EmailStr, field_validator
from .base import ORMBase
from .client_contract import ClientContractRead
 
 
def empty_str_to_none(v):
    if isinstance(v, str) and not v.strip():
        return None
    return v
 
 
class NegotiatorBase(ORMBase):
    name: str
    title: str
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

class NegotiatorCreate(NegotiatorBase):
    pass

class NegotiatorRead(NegotiatorBase):
    negotiator_id: int
    client_id: int

class NegotiatorUpdate(ORMBase):
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class ClientProfileBase(ORMBase):
    company_name: str
    company_email: EmailStr
    company_phone_no: str
    company_address: str
    company_city: str
    company_state: str
    company_zip: str

    negotiators: list[NegotiatorRead] = []
    
    company_logo_url: Optional[str] = None

    @field_validator(
        "company_email",
        mode="before",
    )
    @classmethod
    def normalize_email(cls, v):
        return empty_str_to_none(v)
 
 
class ClientProfileCreate(ClientProfileBase):
    status: str
    negotiators: list[NegotiatorCreate] = []

 
class ClientProfileRead(ClientProfileBase):
    client_id: int
    contract_number: Optional[str] = None
    status: str
    is_deleted: bool
    created_time: datetime
    updated_time: datetime
    contract: Optional[ClientContractRead] = None
 
class ClientListRead(ClientProfileRead):
    has_products: bool
 
class PaginatedClientRead(ORMBase):
    clients: list[ClientListRead]
    total_count: int
    status_counts: dict[str, int]
 
 
class ClientProfileUpdate(ORMBase):
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone_no: Optional[str] = None
    company_address: Optional[str] = None
    company_city: Optional[str] = None
    company_state: Optional[str] = None
    company_zip: Optional[str] = None
 
    negotiators: Optional[list[NegotiatorUpdate]] = None
    is_deleted: Optional[bool] = False
    status: Optional[str] = None
    company_logo_url: Optional[str] = None
 
    @field_validator(
        "company_name",
        "company_email",
        "company_phone_no",
        "company_address",
        "company_city",
        "company_state",
        "company_zip",
        "company_logo_url",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, v):
        return empty_str_to_none(v)
 