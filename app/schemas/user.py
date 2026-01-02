from datetime import datetime
from .base import ORMBase

class UserCreate(ORMBase):
    name: str
    email: str
    phone_no: str
    role_id: int

class UserRead(ORMBase):
    user_id: int
    name: str
    email: str
    phone_no: str
    role_id: int
    created_time: datetime
    updated_time: datetime
