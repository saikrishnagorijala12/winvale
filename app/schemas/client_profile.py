from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from .base import ORMBase


class ClientProfileCreate(ORMBase):
    company_name: str
    company_email: EmailStr          # ✅ validated
    company_phone_no: str
    company_address: str
    company_city: str
    company_state: str
    company_zip: str

    contact_officer_name: str
    contact_officer_email: EmailStr  # ✅ validated
    contact_officer_phone_no: str
    contact_officer_address: str
    contact_officer_city: str
    contact_officer_state: str
    contact_officer_zip: str

    status: int


class ClientProfileRead(ORMBase):
    client_id: int
    company_name: str
    company_email: EmailStr          
    company_phone_no: str
    status: int
    created_time: datetime
    updated_time: datetime


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

    status: Optional[int] = None
