from datetime import datetime
from typing import Dict, Any
from .base import ORMBase

class VendorCreate(ORMBase):
    company_name: str
    company_email: str
    company_phone_no: str
    company_address: Dict[str, Any]
    contact_officer_name: str
    contact_officer_email: str
    contact_officer_phone_no: str
    contact_officer_address: Dict[str, Any]
    status: int

class VendorRead(ORMBase):
    vendor_id: int
    company_name: str
    company_email: str
    company_phone_no: str
    company_address: Dict[str, Any]
    contact_officer_name: str
    contact_officer_email: str
    contact_officer_phone_no: str
    contact_officer_address: Dict[str, Any]
    status: int
    created_time: datetime
    updated_time: datetime
