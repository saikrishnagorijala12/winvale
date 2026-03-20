from datetime import datetime
from typing import Optional
from .base import ORMBase

class ProductHistoryRead(ORMBase):
    product_history_id: int
    product_id: int
    client_id: int

    item_type: str
    item_name: str
    manufacturer: str
    manufacturer_part_number: str
    client_part_number: Optional[str]

    is_current: bool
    effective_start_date: datetime
    effective_end_date: Optional[datetime]
