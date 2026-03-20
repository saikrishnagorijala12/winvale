from datetime import datetime
from .base import ORMBase
from typing import Optional, List, Union
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
    phone_no: Optional[str] = None
    is_active: bool
    is_deleted: bool 
    role: str
    created_time: Optional[datetime] = None

class UserStatusRead(ORMBase):
    registered: bool
    is_active: bool
    Role: Optional[str] = None

class UserAuthRead(UserRead):
    message: Optional[Union[str, tuple]] = None

class UserListRead(ORMBase):
    users: List[UserRead]

class UserUpdate(ORMBase):
    name: Optional[str] = None
    phone_no: Optional[str] = None

class PaginatedUserRead(ORMBase):
    users: List[UserRead]
    total_count: int
    status_counts: dict[str, int]
