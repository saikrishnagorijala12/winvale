import pytest
from unittest.mock import patch, MagicMock, ANY
from tests.conftest import FAKE_ADMIN_USER
from fastapi import status, HTTPException


def _fake_product(**overrides):
    base = {
        "product_id": 1,
        "client_id": 1,
        "client_name": "Acme Corp",
        "item_type": "Product",
        "item_name": "Widget A",
        "item_description": "A high-quality widget",
        "manufacturer": "MFG Corp",
        "manufacturer_part_number": "MPN-001",
        "client_part_number": "VPN-001",
        "sin": "SIN-123",
        "commercial_list_price": 100.00,
        "country_of_origin": "US",
    }
    base.update(overrides)
    return base


def _fake_paginated(items=None, total=None, page=1, page_size=50):
    if items is None:
        items = [_fake_product()]
    if total is None:
        total = len(items)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": items,
    }


class TestGetAllProducts:

    def test_default(self, client, mock_db):
        with patch("app.services.products.get_all", return_value=_fake_paginated()) as mock_service:
            resp = client.get("/products")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=None
        )

    def test_with_search(self, client, mock_db):
        with patch("app.services.products.get_all", return_value=_fake_paginated()) as mock_service:
            resp = client.get("/products?search=widget")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search="widget",
            client_id=None
        )

    def test_with_client_filter(self, client, mock_db):
        with patch("app.services.products.get_all", return_value=_fake_paginated()) as mock_service:
            resp = client.get("/products?client_id=5")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=5
        )

    def test_custom_pagination(self, client, mock_db):
        with patch("app.services.products.get_all", return_value=_fake_paginated(page=2, page_size=10)) as mock_service:
            resp = client.get("/products?page=2&page_size=10")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=2,
            page_size=10,
            search=None,
            client_id=None
        )

    def test_empty_results(self, client, mock_db):
        with patch(
            "app.services.products.get_all",
            return_value=_fake_paginated(items=[], total=0),
        ) as mock_service:
            resp = client.get("/products")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=None
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/products")
        assert resp.status_code in (401, 403)


class TestGetProductByClient:

    def test_success(self, client, mock_db):
        result = {
            "client_id": 5,
            "total": 2,
            "page": 1,
            "page_size": 50,
            "total_pages": 1,
            "items": [_fake_product(), _fake_product(product_id=2)],
        }
        with patch("app.services.products.get_by_client", return_value=result) as mock_service:
            resp = client.get("/products/client/5")
        assert resp.status_code == 200
        assert resp.json()["client_id"] == 5
        assert len(resp.json()["items"]) == 2
        mock_service.assert_called_once_with(
            db=mock_db, client_id=5, page=1, page_size=50, search=None
        )

    def test_not_found(self, client, mock_db):
        with patch(
            "app.services.products.get_by_client",
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No products found for given client",
            ),
        ) as mock_service:
            resp = client.get("/products/client/999")
        assert resp.status_code == 404
        mock_service.assert_called_once_with(
            db=mock_db, client_id=999, page=1, page_size=50, search=None
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/products/client/1")
        assert resp.status_code in (401, 403)
