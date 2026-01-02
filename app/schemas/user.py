from datetime import datetime
from .base import ORMBase
from typing import Optional


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


class UserUpdate(ORMBase):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_no: Optional[str] = None
    role_id: Optional[int] = None
