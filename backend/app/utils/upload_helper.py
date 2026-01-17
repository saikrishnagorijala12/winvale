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

def history_changed(current, row) -> bool:
    for field in HISTORY_FIELDS:
        if getattr(current, field) != row.get(field):
            return True
    return False

