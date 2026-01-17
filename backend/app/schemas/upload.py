from typing import Optional
from .base import ORMBase


class ProductUploadRow(ORMBase):
    item_type: str
    item_name: str
    item_description: Optional[str] = None

    manufacturer: str
    manufacturer_part_number: str
    client_part_number: Optional[str] = None

    sin: Optional[str] = None
    commercial_list_price: Optional[float] = None
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

    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    physical_uom: Optional[str] = None
    weight_lbs: Optional[float] = None
    warranty_period: Optional[int] = None
