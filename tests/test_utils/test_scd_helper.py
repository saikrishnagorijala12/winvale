import pytest
from unittest.mock import MagicMock
from app.utils.scd_helper import create_product_history_snapshot
from app.models.product_history import ProductHistory

def test_create_product_history_snapshot():
    # Mock product object with attributes
    product = MagicMock()
    product.product_id = 101
    product.item_type = "Hardware"
    product.manufacturer = "Dell"
    product.manufacturer_part_number = "CP-123"
    product.vendor_part_number = "V-123"
    product.sin = "SIN-1"
    product.item_name = "Laptop"
    product.item_description = "High performance laptop"
    product.recycled_content_percent = 10.0
    product.uom = "EA"
    product.quantity_per_pack = 1
    product.quantity_unit_uom = "EA"
    product.currency = "USD"
    product.commercial_price = 1200.00
    product.mfc_name = "Dell Inc"
    product.mfc_price = 1000.00
    product.govt_price_no_fee = 1100.00
    product.govt_price_with_fee = 1108.25
    product.country_of_origin = "US"
    product.delivery_days = 5
    product.lead_time_code = "A"
    product.fob_us = "Origin"
    product.fob_ak = ""
    product.fob_hi = ""
    product.fob_pr = ""
    product.nsn = ""
    product.upc = ""
    product.unspsc = ""
    product.sale_price_with_fee = 1105.00
    product.start_date = None
    product.stop_date = None
    product.default_photo = ""
    product.photo_2 = ""
    product.photo_3 = ""
    product.photo_4 = ""
    product.product_url = ""
    product.warranty_period = 1
    product.warranty_unit_of_time = "Y"
    product.length = 12.0
    product.width = 8.0
    product.height = 0.5
    product.physical_uom = "IN"
    product.weight_lbs = 3.5
    product.product_info_code = ""
    product.url_508 = ""
    product.hazmat = False
    product.dealer_cost = 900.00
    product.mfc_markup_percentage = 20.0
    product.govt_markup_percentage = 25.0
    product.row_signature = "sig-123"

    client_id = 1
    snapshot = create_product_history_snapshot(product, client_id, is_current=True)

    assert isinstance(snapshot, ProductHistory)
    assert snapshot.product_id == 101
    assert snapshot.client_id == 1
    assert snapshot.manufacturer == "Dell"
    assert snapshot.is_current is True
    assert snapshot.row_signature == "sig-123"
