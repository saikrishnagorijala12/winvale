from datetime import datetime
from .base import ORMBase
from typing import Optional

class RoleCreate(ORMBase):
    role_name: str

class RoleUpdate(ORMBase):
    role_name: Optional[str] = None

class RoleRead(ORMBase):
    role_id: int
    role_name: str
    created_time: datetime
    updated_time: datetime
