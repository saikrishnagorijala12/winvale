from datetime import datetime
from typing import Optional
from .base import ORMBase

class ProductMasterCreate(ORMBase):
    vendor_id: int
    item_type: str
    item_name: str
    manufacturer: str
    manufacturer_part_number: str
    commercial_list_price: Optional[float] = None

class ProductMasterRead(ORMBase):
    product_id: int
    vendor_id: int
    item_type: str
    item_name: str
    manufacturer: str
    manufacturer_part_number: str
    commercial_list_price: Optional[float]
    created_time: datetime
    updated_time: datetime
