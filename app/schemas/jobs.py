from datetime import datetime
from .base import ORMBase

class JobCreate(ORMBase):
    vendor_id: int
    status: int

class JobRead(ORMBase):
    job_id: int
    vendor_id: int
    status: int
    created_time: datetime
    updated_time: datetime
