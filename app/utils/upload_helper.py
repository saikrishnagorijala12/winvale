import math
import hashlib
from decimal import Decimal, ROUND_HALF_UP

STRING_FIELDS = {
    "item_type",
    "item_name",
    "item_description",
    "manufacturer",
    "manufacturer_part_number",
    "client_part_number",
    "sin",
    "nsn",
    "upc",
    "unspsc",
    "hazmat",
    "product_info_code",
    "uom",
    "quantity_unit_uom",
    "country_of_origin",
    "url_508",
    "product_url",
}

DECIMAL_FIELDS = {
    "commercial_list_price",
    "recycled_content_percent",
}

INTEGER_FIELDS = {
    "quantity_per_pack",
}

MASTER_FIELDS = [
    "item_type",
    "item_name",
    "item_description",
    "manufacturer",
    "manufacturer_part_number",
    "client_part_number",
    "sin",
    "commercial_list_price",
    "country_of_origin",
    "recycled_content_percent",
    "uom",
    "quantity_per_pack",
    "quantity_unit_uom",
    "nsn",
    "upc",
    "unspsc",
    "hazmat",
    "product_info_code",
    "url_508",
    "product_url",
]

HISTORY_FIELDS = [
    "item_type",
    "item_name",
    "item_description",
    "manufacturer",
    "manufacturer_part_number",
    "client_part_number",
    "sin",
    "country_of_origin",
    "recycled_content_percent",
    "uom",
    "quantity_per_pack",
    "quantity_unit_uom",
    "nsn",
    "upc",
    "unspsc",
    "hazmat",
    "product_info_code",
    "url_508",
    "product_url",
]

DIM_FIELDS = [
    "length",
    "width",
    "height",
    "physical_uom",
    "weight_lbs",
    "warranty_period",
    "photo_type",
    "photo_path",
]

def normalize(value, field_name):
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if field_name in STRING_FIELDS:
        return str(value).strip()

    if field_name in INTEGER_FIELDS:
        try:
            return int(value)
        except Exception:
            return None

    if field_name in DECIMAL_FIELDS:
        try:
            return Decimal(str(value)).quantize(
                Decimal("0.00"), rounding=ROUND_HALF_UP
            )
        except Exception:
            return None

    return str(value).strip()


def identity_signature(row: dict) -> str:
    payload = f"{row.get('manufacturer')}|{row.get('manufacturer_part_number')}"
    return hashlib.sha256(payload.encode()).hexdigest()


def history_signature(row: dict) -> str:
    parts = []
    for f in HISTORY_FIELDS:
        v = row.get(f)
        parts.append("" if v is None else str(v))
    return hashlib.sha256("|".join(parts).encode()).hexdigest()
