from datetime import datetime
from .base import ORMBase

class StatusCreate(ORMBase):
    status_code: str

class StatusRead(ORMBase):
    status_id: int
    status_code: str
    created_time: datetime
