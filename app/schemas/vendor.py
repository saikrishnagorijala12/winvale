from datetime import datetime
from typing import Dict, Any,Optional
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

class VendorUpdate(ORMBase):
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    company_phone_no: Optional[str] = None
    company_address: Optional[Dict[str, Any]] = None

    contact_officer_name: Optional[str] = None
    contact_officer_email: Optional[str] = None
    contact_officer_phone_no: Optional[str] = None
    contact_officer_address: Optional[Dict[str, Any]] = None

    status: Optional[int] = None