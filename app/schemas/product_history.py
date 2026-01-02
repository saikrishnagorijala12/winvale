from datetime import datetime
from typing import Optional
from .base import ORMBase

class ProductHistoryRead(ORMBase):
    product_history_id: int
    product_id: int
    vendor_id: int
    item_name: str
    manufacturer: str
    manufacturer_part_number: str
    commercial_list_price: Optional[float]
    is_current: bool
    effective_start_date: datetime
    effective_end_date: Optional[datetime]
