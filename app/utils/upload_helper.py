import math
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime


STRING_FIELDS = {
    "item_type",
    "manufacturer",
    "manufacturer_part_number",
    "vendor_part_number",
    "sin",
    "item_name",
    "item_description",
    "uom",
    "quantity_unit_uom",
    "mfc_name",
    "country_of_origin",
    "lead_time_code",
    "fob_us",
    "fob_ak",
    "fob_hi",
    "fob_pr",
    "nsn",
    "upc",
    "unspsc",
    "default_photo",
    "photo_2",
    "photo_3",
    "photo_4",
    "product_url",
    "warranty_unit_of_time",
    "physical_uom",
    "product_info_code",
    "url_508",
    "hazmat",
}

INTEGER_FIELDS = {
    "quantity_per_pack",
    "delivery_days",
    "warranty_period",
}

DECIMAL_FIELDS = {
    "recycled_content_percent",
    "commercial_price",
    "mfc_price",
    "govt_price_no_fee",
    "govt_price_with_fee",
    "sale_price_with_fee",
    "dealer_cost",
    "mfc_markup_percentage",
    "govt_markup_percentage",
    "length",
    "width",
    "height",
    "weight_lbs",
}

DATE_FIELDS = {
    "start_date",
    "stop_date",
}

DEFAULT_VALUES = {
    "currency": "USD",
}


MASTER_FIELDS = [
    "item_type",
    "manufacturer",
    "manufacturer_part_number",
    "vendor_part_number",
    "sin",
    "item_name",
    "item_description",
    "recycled_content_percent",
    "uom",
    "quantity_per_pack",
    "quantity_unit_uom",
    "currency",
    "commercial_price",
    "mfc_name",
    "mfc_price",
    "govt_price_no_fee",
    "govt_price_with_fee",
    "country_of_origin",
    "delivery_days",
    "lead_time_code",
    "fob_us",
    "fob_ak",
    "fob_hi",
    "fob_pr",
    "nsn",
    "upc",
    "unspsc",
    "sale_price_with_fee",
    "start_date",
    "stop_date",
    "default_photo",
    "photo_2",
    "photo_3",
    "photo_4",
    "product_url",
    "warranty_period",
    "warranty_unit_of_time",
    "product_info_code",
    "url_508",
    "hazmat",
    "dealer_cost",
    "mfc_markup_percentage",
    "govt_markup_percentage",
]

HISTORY_FIELDS = MASTER_FIELDS[:]  # exact mirror

DIM_FIELDS = [
    "length",
    "width",
    "height",
    "physical_uom",
    "weight_lbs",
]


def normalize(value, field_name):
    # Handle missing / NaN values FIRST
    if value is None:
        return DEFAULT_VALUES.get(field_name)

    if isinstance(value, float) and math.isnan(value):
        return DEFAULT_VALUES.get(field_name)

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
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except Exception:
            return None

    if field_name in DATE_FIELDS:
        if isinstance(value, (date, datetime)):
            return value.date() if isinstance(value, datetime) else value
        return None

    return value





def identity_signature(row: dict) -> str:
    """
    Identity = what makes a product unique forever
    """
    payload = f"{row.get('manufacturer')}|{row.get('manufacturer_part_number')}"
    return hashlib.sha256(payload.encode()).hexdigest()


def history_signature(row: dict) -> str:
    """
    History = any business-relevant change
    """
    parts = []
    for f in HISTORY_FIELDS:
        v = row.get(f)
        parts.append("" if v is None else str(v))
    return hashlib.sha256("|".join(parts).encode()).hexdigest()
