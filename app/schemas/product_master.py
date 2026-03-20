from datetime import datetime
from typing import Optional, List
from .base import ORMBase

class ProductMasterCreate(ORMBase):
    client_id: int
    item_type: str
    item_name: str
    manufacturer: str
    manufacturer_part_number: str
    client_part_number: Optional[str] = None
    commercial_list_price: Optional[float] = None

class ProductMasterRead(ORMBase):
    product_id: int
    client_id: int
    item_type: str
    item_name: str
    manufacturer: str
    manufacturer_part_number: str
    client_part_number: Optional[str] = None
    commercial_list_price: Optional[float] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

class ProductReadFull(ProductMasterRead):
    client_name: Optional[str] = None
    item_description: Optional[str] = None
    sin: Optional[str] = None
    country_of_origin: Optional[str] = None
    recycled_content_percent: Optional[float] = None
    uom: Optional[str] = None
    quantity_per_pack: Optional[int] = None
    quantity_unit_uom: Optional[str] = None
    nsn: Optional[str] = None
    upc: Optional[str] = None
    unspsc: Optional[str] = None
    hazmat: Optional[str] = None
    product_info_code: Optional[str] = None
    url_508: Optional[str] = None
    product_url: Optional[str] = None
    row_signature: Optional[str] = None
    
    # Dimension fields
    dim_id: Optional[int] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    physical_uom: Optional[str] = None
    weight_lbs: Optional[float] = None
    warranty_period: Optional[int] = None
    photo_type: Optional[str] = None
    photo_path: Optional[str] = None
    dim_created_time: Optional[datetime] = None
    dim_updated_time: Optional[datetime] = None

class ProductPaginationRead(ORMBase):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ProductReadFull]
    client_id: Optional[int] = None

class ProductMasterUpdate(ORMBase):
    item_type: Optional[str] = None
    item_name: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    client_part_number: Optional[str] = None
    commercial_list_price: Optional[float] = None
