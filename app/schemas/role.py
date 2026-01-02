from datetime import datetime
from .base import ORMBase

class RoleCreate(ORMBase):
    role_name: str

class RoleRead(ORMBase):
    role_id: int
    role_name: str
    created_time: datetime
    updated_time: datetime
