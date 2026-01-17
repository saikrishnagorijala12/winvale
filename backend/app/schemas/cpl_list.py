from datetime import datetime
from typing import Optional
from .base import ORMBase

class CPLCreate(ORMBase):
    client_id: int
    manufacturer_name: str
    manufacturer_part_number: str
    item_name: str
    commercial_list_price: Optional[float]

class CPLRead(ORMBase):
    cpl_id: int
    client_id: int
    manufacturer_name: str
    item_name: str
    commercial_list_price: Optional[float]
    created_time: datetime
