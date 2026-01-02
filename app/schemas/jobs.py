from datetime import datetime
from .base import ORMBase
from typing import Optional


class JobCreate(ORMBase):
    vendor_id: int
    status: int

class JobUpdate(ORMBase):
    status: Optional[int] = None

class JobRead(ORMBase):
    job_id: int
    vendor_id: int
    status: int
    created_time: datetime
    updated_time: datetime
