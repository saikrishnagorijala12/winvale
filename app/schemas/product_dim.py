from datetime import datetime
from typing import Optional
from .base import ORMBase

class ProductDimCreate(ORMBase):
    product_id: int
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    physical_uom: Optional[str]
    weight_lbs: Optional[float]
    warranty_period: Optional[int]

class ProductDimRead(ORMBase):
    dim_id: int
    product_id: int
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    physical_uom: Optional[str]
    weight_lbs: Optional[float]
    warranty_period: Optional[int]
    created_time: datetime
    updated_time: datetime

class ProductDimUpdate(ORMBase):
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    physical_uom: Optional[str] = None
    weight_lbs: Optional[float] = None
    warranty_period: Optional[int] = None
