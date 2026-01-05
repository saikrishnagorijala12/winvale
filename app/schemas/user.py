from datetime import datetime
from .base import ORMBase
from typing import Optional
from pydantic import EmailStr


class UserCreate(ORMBase):
    name: str
    email: EmailStr
    phone_no: str
    role_id: int

class UserRead(ORMBase):
    user_id: int
    name: str
    email: EmailStr
    phone_no: str
    role_id: int
    created_time: datetime
    updated_time: datetime


class UserUpdate(ORMBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    role_id: Optional[int] = None
