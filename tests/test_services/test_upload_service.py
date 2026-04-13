import pytest
from unittest.mock import MagicMock, patch
from app.services.upload import _process_batch

@pytest.fixture
def mock_db():
    return MagicMock()

def test_process_batch_insert(mock_db):
    client_id = 1
    batch_data = [
        {
            "manufacturer": "Apple",
            "manufacturer_part_number": "iPhone15",
            "item_name": "iPhone 15",
            # ... other fields
        }
    ]
    product_lookup = {}
    history_lookup = {}
    seen_product_ids = set()

    # Mock DB execution for returning product_id
    mock_db.execute().all.return_value = [(101, "Apple", "iPhone15")]

    with patch("app.services.upload.identity_signature", return_value="sig1"):
        with patch("app.services.upload.history_signature", return_value="hsig1"):
            inserted, updated, reactivated, skipped = _process_batch(
                mock_db, client_id, batch_data, product_lookup, history_lookup, seen_product_ids,
                0, 0, 0, 0
            )

            assert inserted == 1
            mock_db.execute.assert_called()

def test_process_batch_update(mock_db):
    client_id = 1
    batch_data = [
        {
            "manufacturer": "Apple",
            "manufacturer_part_number": "iPhone15",
            "item_name": "iPhone 15 Updated",
        }
    ]
    product_id = 101
    product_lookup = {("Apple", "iPhone15"): (product_id, "sig1", False, None)}
    history_lookup = {product_id: "old_hsig"}
    seen_product_ids = set()

    with patch("app.services.upload.identity_signature", return_value="sig1"):
        with patch("app.services.upload.history_signature", return_value="new_hsig"):
            inserted, updated, reactivated, skipped = _process_batch(
                mock_db, client_id, batch_data, product_lookup, history_lookup, seen_product_ids,
                0, 0, 0, 0
            )

            assert updated == 1
            assert product_id in seen_product_ids
            mock_db.bulk_update_mappings.assert_called()
