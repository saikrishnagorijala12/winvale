from datetime import datetime
from typing import Optional
from pydantic import EmailStr, field_validator
from .base import ORMBase
 
 
def empty_str_to_none(v):
    if isinstance(v, str) and not v.strip():
        return None
    return v
 
 
class ClientProfileBase(ORMBase):
    company_name: str
    company_email: EmailStr
    company_phone_no: str
    company_address: str
    company_city: str
    company_state: str
    company_zip: str
 
    contact_officer_name: Optional[str] = None
    contact_officer_email: Optional[EmailStr] = None
    contact_officer_phone_no: Optional[str] = None
    contact_officer_address: Optional[str] = None
    contact_officer_city: Optional[str] = None
    contact_officer_state: Optional[str] = None
    contact_officer_zip: Optional[str] = None
    is_deleted: Optional[bool] = False
    created_time: datetime
    updated_time: datetime
 
    status: str
 
    @field_validator(
        "contact_officer_name",
        "contact_officer_email",
        "contact_officer_phone_no",
        "contact_officer_address",
        "contact_officer_city",
        "contact_officer_state",
        "contact_officer_zip",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, v):
        return empty_str_to_none(v)
 
 
class ClientProfileCreate(ClientProfileBase):
    pass
 
 
class ClientProfileRead(ClientProfileBase):
    client_id: int
    created_time: datetime
    updated_time: datetime
 
 
class ClientListRead(ClientProfileBase):
    client_id: int
    
 
 
class ClientProfileUpdate(ORMBase):
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone_no: Optional[str] = None
    company_address: Optional[str] = None
    company_city: Optional[str] = None
    company_state: Optional[str] = None
    company_zip: Optional[str] = None
 
    contact_officer_name: Optional[str] = None
    contact_officer_email: Optional[EmailStr] = None
    contact_officer_phone_no: Optional[str] = None
    contact_officer_address: Optional[str] = None
    contact_officer_city: Optional[str] = None
    contact_officer_state: Optional[str] = None
    contact_officer_zip: Optional[str] = None
    is_deleted: Optional[bool] = False
    status: Optional[str] = None
 
    @field_validator(
        "company_name",
        "company_email",
        "company_phone_no",
        "company_address",
        "company_city",
        "company_state",
        "company_zip",
        "contact_officer_name",
        "contact_officer_email",
        "contact_officer_phone_no",
        "contact_officer_address",
        "contact_officer_city",
        "contact_officer_state",
        "contact_officer_zip",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, v):
        return empty_str_to_none(v)
 