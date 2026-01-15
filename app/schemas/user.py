from datetime import datetime
from .base import ORMBase
from typing import Optional
from pydantic import EmailStr


class UserCreate(ORMBase):
    name: str
    email: EmailStr
    phone_no: Optional[str]
    is_active: Optional[bool] = False
    is_deleted: Optional[bool] = False
    cognito_sub : str
    role_name: str

class UserRead(ORMBase):
    user_id: int
    name: str
    email: EmailStr
    phone_no: str
    is_active: Optional[bool] = False
    is_deleted: Optional[bool] = False 
    role_name: int
    cognito_sub : str
    created_time: datetime
    updated_time: datetime


class UserUpdate(ORMBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    is_active: Optional[bool] = False
    is_deleted: Optional[bool] = False
    cognito_sub : Optional[str]
    role_id: Optional[str] = None
