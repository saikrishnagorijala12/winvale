from datetime import datetime
from .base import ORMBase
from typing import Optional
from pydantic import EmailStr


class UserCreate(ORMBase):
    name: str
    email: EmailStr
    phone_no: str
    is_active: Optional[bool] = False
    role_id: int

class UserRead(ORMBase):
    user_id: int
    name: str
    email: EmailStr
    phone_no: str
    is_active: Optional[bool] = False 
    role_id: int
    created_time: datetime
    updated_time: datetime


class UserUpdate(ORMBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    is_active: Optional[bool] = False
    role_id: Optional[int] = None
