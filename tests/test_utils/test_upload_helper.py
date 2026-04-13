import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch
from app.utils.upload_helper import (
    normalize,
    identity_signature,
    history_signature,
    set_upload_status,
    get_upload_status,
)

def test_normalize_string():
    assert normalize("  test  ", "item_name") == "test"
    assert normalize(123, "item_name") == "123"
    assert normalize(None, "item_name") is None

def test_normalize_integer():
    assert normalize("10", "quantity_per_pack") == 10
    assert normalize(10.5, "quantity_per_pack") == 10
    assert normalize("invalid", "quantity_per_pack") is None

def test_normalize_decimal():
    assert normalize("10.5", "commercial_price") == Decimal("10.50")
    assert normalize(10.555, "commercial_price") == Decimal("10.56")
    assert normalize("invalid", "commercial_price") is None

def test_normalize_date():
    d = date(2023, 1, 1)
    assert normalize(d, "start_date") == d
    assert normalize(None, "start_date") is None

def test_normalize_default_values():
    assert normalize(None, "currency") == "USD"
    import math
    assert normalize(math.nan, "currency") == "USD"

def test_identity_signature():
    row = {"manufacturer": "Apple", "manufacturer_part_number": "iPhone15"}
    sig1 = identity_signature(row)
    sig2 = identity_signature(row)
    assert sig1 == sig2
    assert len(sig1) == 64  # SHA256 length

def test_history_signature():
    row1 = {"manufacturer": "Apple", "manufacturer_part_number": "iPhone15", "commercial_price": 999.99}
    row2 = {"manufacturer": "Apple", "manufacturer_part_number": "iPhone15", "commercial_price": 899.99}
    assert history_signature(row1) != history_signature(row2)

@patch("app.utils.upload_helper.redis_client")
def test_set_upload_status(mock_redis):
    set_upload_status(1, {"status": "processing"})
    mock_redis.setex.assert_called_once()

@patch("app.utils.upload_helper.redis_client")
def test_get_upload_status(mock_redis):
    mock_redis.get.return_value = '{"status": "completed"}'
    status = get_upload_status(1)
    assert status == {"status": "completed"}
    mock_redis.get.assert_called_once()
