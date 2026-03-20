from typing import Dict, Optional
from .base import ORMBase

class CPLUploadSummary(ORMBase):
    new_products: int
    removed_products: int
    price_increase: int
    price_decrease: int
    description_changed: int
    name_changed: int
    no_change: int

class CPLUploadResponse(ORMBase):
    job_id: int
    client_id: int
    status: str
    summary: CPLUploadSummary
    next_step: str
