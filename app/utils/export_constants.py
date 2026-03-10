# --- Header Definitions for Export Services ---

# 1. Price Modification Export (Detailed Format for Price Increase/Decrease)
PRICE_CHANGE_HEADERS = [
    "item_type", "manufacturer", "manufacturer_part_number",
    "vendor_part_number", "sin", "item_name", "item_description",
    "recycled_content_percent", "uom", "quantity_per_pack",
    "quantity_unit_uom", "old_commercial_price", "new_commercial_price", "percentage_change", "mfc_name", "mfc_price",
    "govt_price_no_fee", "govt_price_with_fee", "country_of_origin",
    "delivery_days", "lead_time_code", "fob_us", "fob_ak",
    "fob_hi", "fob_pr", "nsn", "upc", "unspsc",
    "sale_price_with_fee", "start_date", "stop_date",
    "default_photo", "photo_2", "photo_3", "photo_4",
    "product_url", "warranty_period", "warranty_unit_of_time",
    "length", "width", "height", "physical_uom", "weight_lbs",
    "product_info_code", "url_508", "hazmat",
    "dealer_cost", "mfc_markup_percentage",
    "govt_markup_percentage",
]

PRICE_CHANGE_GROUP_ROW = [
    "Base Product or Accessory",
    "Manufacturer Information", "",
    "Vendor Part Number",
    "Special Item Number",
    "Product Information", "", "",
    "Unit of Measure",
    "Quantity Per Pack", "",
    "Commercial Price / Manufacturer's Suggested Retail Price", "", "",
    "Most Favored Customer", "",
    "Price Proposal", "",
    "Country of Origin",
    "Delivery Information", "", "", "", "", "",
    "National Stock Number",
    "UPC",
    "United Nations Standard Products and Services Code",
    "Temporary Price Reduction (TPR)", "", "",
    "Photo File References", "", "", "", "",
    "Warranty Duration", "",
    "Product Dimensions", "", "", "", "",
    "Product Information / Categorization", "", "",
    "Dealer Markup", "", ""
]

PRICE_CHANGE_MERGES = [
    (2, 3), (6, 8), (10, 11), (12, 14), (15, 16),
    (17, 18), (20, 25), (29, 31),
    (32, 36), (37, 38), (39, 43),
    (44, 46), (47, 49)
]

# 2. Price Modification Export (Standard Format for Additions/Deletions/etc)
STANDARD_MODIFICATION_HEADERS = [
    "item_type", "manufacturer", "manufacturer_part_number",
    "vendor_part_number", "sin", "item_name", "item_description",
    "recycled_content_percent", "uom", "quantity_per_pack",
    "quantity_unit_uom", "commercial_price", "mfc_name", "mfc_price",
    "govt_price_no_fee", "govt_price_with_fee", "country_of_origin",
    "delivery_days", "lead_time_code", "fob_us", "fob_ak",
    "fob_hi", "fob_pr", "nsn", "upc", "unspsc",
    "sale_price_with_fee", "start_date", "stop_date",
    "default_photo", "photo_2", "photo_3", "photo_4",
    "product_url", "warranty_period", "warranty_unit_of_time",
    "length", "width", "height", "physical_uom", "weight_lbs",
    "product_info_code", "url_508", "hazmat",
    "dealer_cost", "mfc_markup_percentage",
    "govt_markup_percentage",
]

STANDARD_MODIFICATION_GROUP_ROW = [
    "Base Product or Accessory",
    "Manufacturer Information", "",
    "Vendor Part Number",
    "Special Item Number",
    "Product Information", "", "",
    "Unit of Measure",
    "Quantity Per Pack", "",
    "Commercial Price / Manufacturer's Suggested Retail Price",
    "Most Favored Customer", "",
    "Price Proposal", "",
    "Country of Origin",
    "Delivery Information", "", "", "", "", "",
    "National Stock Number",
    "UPC",
    "United Nations Standard Products and Services Code",
    "Temporary Price Reduction (TPR)", "", "",
    "Photo File References", "", "", "", "",
    "Warranty Duration", "",
    "Product Dimensions", "", "", "", "",
    "Product Information / Categorization", "", "",
    "Dealer Markup", "", ""
]

STANDARD_MODIFICATION_MERGES = [
    (2, 3), (6, 8), (10, 11), (13, 14),
    (15, 16), (18, 23), (27, 29),
    (30, 34), (35, 36), (37, 41),
    (42, 44), (45, 47)
]

# 3. Product Master Export
PRODUCT_EXPORT_HEADERS = [
    "item_type", "manufacturer", "manufacturer_part_number",
    "vendor_part_number", "sin", "item_name", "item_description",
    "recycled_content_percent", "uom", "quantity_per_pack",
    "quantity_unit_uom", "commercial_price", "mfc_name", "mfc_price",
    "govt_price_no_fee", "govt_price_with_fee", "country_of_origin",
    "delivery_days", "lead_time_code", "fob_us", "fob_ak",
    "fob_hi", "fob_pr", "nsn", "upc", "unspsc",
    "sale_price_with_fee", "start_date", "stop_date",
    "default_photo", "photo_2", "photo_3", "photo_4",
    "product_url", "warranty_period", "warranty_unit_of_time",
    "length", "width", "height", "physical_uom", "weight_lbs",
    "product_info_code", "url_508", "hazmat",
    "dealer_cost", "mfc_markup_percentage",
    "govt_markup_percentage",
]

PRODUCT_EXPORT_GROUP_ROW = [
    "Base Product or Accessory",
    "Manufacturer Information", "",
    "Vendor Part Number",
    "Special Item Number",
    "Product Information", "", "",
    "Unit of Measure",
    "Quantity Per Pack", "",
    "Commercial Price / Manufacturer's Suggested Retail Price",
    "Most Favored Customer", "",
    "Price Proposal", "",
    "Country of Origin",
    "Delivery Information", "", "", "", "", "",
    "National Stock Number",
    "UPC",
    "United Nations Standard Products and Services Code",
    "Temporary Price Reduction (TPR)", "", "",
    "Photo File References", "", "", "", "",
    "Warranty Duration", "",
    "Product Dimensions", "", "", "", "",
    "Product Information / Categorization", "", "",
    "Dealer Markup", "", ""
]

PRODUCT_EXPORT_MERGES = [
    (2, 3), (6, 8), (10, 11), (13, 14),
    (15, 16), (18, 23), (27, 29),
    (30, 34), (35, 36), (37, 41),
    (42, 44), (45, 47)
]
