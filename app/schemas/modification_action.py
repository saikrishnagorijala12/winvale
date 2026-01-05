from datetime import datetime
from typing import Optional
from .base import ORMBase

class ModificationActionRead(ORMBase):
    action_id: int
    user_id: int
    client_id: int
    job_id: int
    action_type: str
    old_price: Optional[float]
    new_price: Optional[float]
    number_of_items_impacted: int
    created_time: datetime
