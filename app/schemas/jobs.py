from datetime import datetime
from typing import Optional
from .base import ORMBase

class JobCreate(ORMBase):
    client_id: int
    status: int

class JobRead(ORMBase):
    job_id: int
    client_id: int
    status: int
    created_time: datetime
    updated_time: datetime

class JobUpdate(ORMBase):
    status: Optional[int] = None
