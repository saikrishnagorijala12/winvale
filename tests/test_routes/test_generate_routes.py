
import pytest
from unittest.mock import patch, ANY
from fastapi import HTTPException, status
from tests.conftest import FAKE_ADMIN_USER


def _fake_job_details(**overrides):
    base = {
        "job_id": 1,
        "client": {"client_id": 1, "company_name": "Acme Corp"},
        "client_contract": {
            "contract_officer_name": "Jane Doe",
            "contract_number": "GS-35F-0001",
            "discounts": {
                "gsa_proposed_discount": 15.0,
                "q_v_discount": "5%",
            },
            "delivery": {
                "normal_delivery_time": 30,
                "expedited_delivery_time": 10,
            },
            "address": {
                "contract_officer_address": "456 Oak Ave",
                "contract_officer_city": "DC",
                "contract_officer_state": "DC",
                "contract_officer_zip": "20001",
            },
            "other": {
                "fob_term": "Destination",
                "energy_star_compliance": "Yes",
                "additional_concessions": "None",
            },
        },
        "modification_summary": {
            "products_added": 2,
            "products_deleted": 0,
            "description_changed": 1,
            "price_increased": 1,
            "price_decreased": 0,
        },
    }
    base.update(overrides)
    return base


class TestGetJobDetails:

    def test_success(self, client, mock_db):
        with patch(
            "app.services.generate.get_job_full_details",
            return_value=_fake_job_details(),
        ) as mock_service:
            resp = client.get("/generate/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == 1
        assert "modification_summary" in data
        assert "client_contract" in data
        mock_service.assert_called_once_with(
            db=mock_db,
            job_id=1,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_job_not_found(self, client, mock_db):
        with patch(
            "app.services.generate.get_job_full_details",
            side_effect=HTTPException(status_code=404, detail="Job not found"),
        ) as mock_service:
            resp = client.get("/generate/999")
        assert resp.status_code == 404
        mock_service.assert_called_once_with(
            db=mock_db,
            job_id=999,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_invalid_user(self, client, mock_db):
        with patch(
            "app.services.generate.get_job_full_details",
            side_effect=HTTPException(status_code=401, detail="Invalid user"),
        ) as mock_service:
            resp = client.get("/generate/1")
        assert resp.status_code == 401
        mock_service.assert_called_once_with(
            db=mock_db,
            job_id=1,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_no_contract(self, client, mock_db):
        details = _fake_job_details(client_contract=None)
        with patch(
            "app.services.generate.get_job_full_details",
            return_value=details,
        ) as mock_service:
            resp = client.get("/generate/1")
        assert resp.status_code == 200
        assert resp.json()["client_contract"] is None
        mock_service.assert_called_once_with(
            db=mock_db,
            job_id=1,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/generate/1")
        assert resp.status_code in (401, 403)
