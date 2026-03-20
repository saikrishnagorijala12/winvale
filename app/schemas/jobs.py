from datetime import datetime
from typing import Optional, List, Dict
from .base import ORMBase

class JobCreate(ORMBase):
    client_id: int
    status: str

class JobCreateResponse(ORMBase):
    job_id: int
    client_id: int
    status: str
    created_time: datetime

class JobRead(ORMBase):
    job_id: int
    client_id: int
    contract_number: Optional[str] = None
    client: Optional[str] = None
    client_logo_url: Optional[str] = None
    user_id: int
    user: Optional[str] = None
    status: str
    action_summary: Dict[str, int] = {}
    created_time: datetime
    updated_time: Optional[datetime] = None

class JobPaginationRead(ORMBase):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[JobRead]

class JobActionRead(ORMBase):
    action_id: int
    action_type: str
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    old_price: Optional[float] = None
    new_price: Optional[float] = None
    old_description: Optional[str] = None
    new_description: Optional[str] = None
    number_of_items_impacted: int
    created_time: datetime

class JobWithActionsRead(JobRead):
    modifications_actions: List[JobActionRead]
    total_actions: int
    total_pages: int

class JobUpdate(ORMBase):
    status: Optional[str] = None

class JobApproveResponse(ORMBase):
    job_id: int
    status: str
    message: str
