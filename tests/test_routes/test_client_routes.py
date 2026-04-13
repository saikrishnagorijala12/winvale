import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi import status, HTTPException
from datetime import datetime, timezone

from tests.conftest import FAKE_ADMIN_USER


NOW = datetime.now(timezone.utc).isoformat()


def _fake_client(**overrides):
    base = {
        "client_id": 1,
        "company_name": "Acme Corp",
        "company_email": "info@acme.com",
        "company_phone_no": "5551234567",
        "company_address": "123 Main St",
        "company_city": "Springfield",
        "company_state": "IL",
        "company_zip": "62701",
        "contact_officer_name": None,
        "contact_officer_email": None,
        "contact_officer_phone_no": None,
        "contact_officer_address": None,
        "contact_officer_city": None,
        "contact_officer_state": None,
        "contact_officer_zip": None,
        "contract_number": None,
        "status": "pending",
        "is_deleted": False,
        "has_products": False,
        "created_time": NOW,
        "updated_time": NOW,
    }
    base.update(overrides)
    return base


VALID_CLIENT_PAYLOAD = {
    "company_name": "Acme Corp",
    "company_email": "info@acme.com",
    "company_phone_no": "5551234567",
    "company_address": "123 Main St",
    "company_city": "Springfield",
    "company_state": "IL",
    "company_zip": "62701",
    "status": "pending",
}


class TestGetAllClients:

    def test_success(self, client, mock_db):
        with patch(
            "app.services.clients.get_all_clients",
            return_value={
                "clients": [_fake_client()],
                "total_count": 1,
                "status_counts": {"all": 1, "pending": 1, "approved": 0, "rejected": 0},
            },
        ) as mock_service:
            resp = client.get("/clients")
        assert resp.status_code == 200
        data = resp.json()
        assert "clients" in data
        assert len(data["clients"]) == 1
        mock_service.assert_called_once_with(
            db=mock_db, skip=0, limit=10, status="all", search=None
        )

    def test_empty_list(self, client, mock_db):
        with patch(
            "app.services.clients.get_all_clients",
            return_value={
                "clients": [],
                "total_count": 0,
                "status_counts": {"all": 0, "pending": 0, "approved": 0, "rejected": 0},
            },
        ) as mock_service:
            resp = client.get("/clients")
        assert resp.status_code == 200
        assert resp.json()["clients"] == []
        mock_service.assert_called_once_with(
            db=mock_db, skip=0, limit=10, status="all", search=None
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/clients")
        assert resp.status_code in (401, 403)


class TestGetActiveClients:

    def test_success(self, client, mock_db):
        fake = _fake_client(status="approved", has_products=True)
        with patch("app.services.clients.get_active_clients", return_value=[fake]) as mock_service:
            resp = client.get("/clients/approved")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data[0]["status"] == "approved"
        mock_service.assert_called_once_with(mock_db)

    def test_empty(self, client, mock_db):
        with patch("app.services.clients.get_active_clients", return_value=[]) as mock_service:
            resp = client.get("/clients/approved")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(mock_db)


class TestGetClientById:

    def test_success(self, client, mock_db):
        fake = _fake_client(client_id=42)
        with patch("app.services.clients.get_client_by_id", return_value=fake) as mock_service:
            resp = client.get("/clients/42")
        assert resp.status_code == 200
        assert resp.json()["client_id"] == 42
        mock_service.assert_called_once_with(mock_db, 42)

    def test_not_found(self, client, mock_db):
        with patch("app.services.clients.get_client_by_id", return_value=None) as mock_service:
            resp = client.get("/clients/999")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()
        mock_service.assert_called_once_with(mock_db, 999)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/clients/1")
        assert resp.status_code in (401, 403)



class TestCreateClient:

    def test_success(self, client, mock_db):
        fake = _fake_client(client_id=10)
        with patch("app.services.clients.create_client_profile", return_value=fake) as mock_service:
            resp = client.post("/clients", json=VALID_CLIENT_PAYLOAD)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["client_id"] == 10
        mock_service.assert_called_once_with(mock_db, ANY, FAKE_ADMIN_USER)

    def test_value_error(self, client, mock_db):
        with patch(
            "app.services.clients.create_client_profile",
            side_effect=ValueError("Duplicate phone number"),
        ) as mock_service:
            resp = client.post("/clients", json=VALID_CLIENT_PAYLOAD)
        assert resp.status_code == 400
        mock_service.assert_called_once_with(mock_db, ANY, FAKE_ADMIN_USER)

    def test_validation_missing_company_name(self, client):
        bad = {**VALID_CLIENT_PAYLOAD}
        del bad["company_name"]
        resp = client.post("/clients", json=bad)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_validation_invalid_email(self, client):
        bad = {**VALID_CLIENT_PAYLOAD, "company_email": "bad-email"}
        resp = client.post("/clients", json=bad)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_validation_empty_body(self, client):
        resp = client.post("/clients", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post("/clients", json=VALID_CLIENT_PAYLOAD)
        assert resp.status_code in (401, 403)



class TestUpdateClient:

    def test_success(self, client, mock_db):
        fake = _fake_client(company_name="Updated Corp")
        with patch("app.services.clients.update_client", return_value=fake) as mock_service:
            resp = client.put("/clients/1", json={"company_name": "Updated Corp"})
        assert resp.status_code == 200
        assert resp.json()["company_name"] == "Updated Corp"
        mock_service.assert_called_once_with(db=mock_db, client_id=1, data=ANY)

    def test_not_found(self, client, mock_db):
        with patch("app.services.clients.update_client", return_value=None) as mock_service:
            resp = client.put("/clients/999", json={"company_name": "X"})
        assert resp.status_code == 404
        mock_service.assert_called_once_with(db=mock_db, client_id=999, data=ANY)

    def test_value_error(self, client, mock_db):
        with patch(
            "app.services.clients.update_client",
            side_effect=ValueError("Duplicate data"),
        ) as mock_service:
            resp = client.put("/clients/1", json={"company_name": "X"})
        assert resp.status_code == 400
        mock_service.assert_called_once_with(db=mock_db, client_id=1, data=ANY)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.put("/clients/1", json={"company_name": "X"})
        assert resp.status_code in (401, 403)


class TestUpdateClientStatus:

    def test_approve_success(self, client, mock_db):
        with patch("app.routes.clients.require_admin", return_value=True):
            with patch("app.services.clients.update_client_status") as mock_service:
                resp = client.patch("/clients/1/approve?action=approve")
        assert resp.status_code == 200
        assert "approved" in resp.json()["message"].lower()
        mock_service.assert_called_once_with(db=mock_db, client_id=1, action="approve")

    def test_reject_success(self, client, mock_db):
        with patch("app.routes.clients.require_admin", return_value=True):
            with patch("app.services.clients.update_client_status") as mock_service:
                resp = client.patch("/clients/1/approve?action=reject")
        assert resp.status_code == 200

        assert "rejectd" in resp.json()["message"].lower()
        mock_service.assert_called_once_with(db=mock_db, client_id=1, action="reject")

    def test_client_not_found(self, client, mock_db):
        from app.services.clients import ClientNotFoundError

        with patch("app.routes.clients.require_admin", return_value=True):
            with patch(
                "app.services.clients.update_client_status",
                side_effect=ClientNotFoundError(),
            ) as mock_service:
                resp = client.patch("/clients/999/approve?action=approve")
        assert resp.status_code == 404
        mock_service.assert_called_once_with(db=mock_db, client_id=999, action="approve")

    def test_invalid_action(self, client):
        resp = client.patch("/clients/1/approve?action=suspend")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_missing_action(self, client):
        resp = client.patch("/clients/1/approve")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_non_admin_forbidden(self, regular_client):
        with patch(
            "app.routes.clients.require_admin",
            side_effect=HTTPException(status_code=403, detail="Admin only"),
        ):
            resp = regular_client.patch("/clients/1/approve?action=approve")
        assert resp.status_code == 403


class TestDeleteClient:

    def test_success(self, client, mock_db):
        fake = _fake_client(is_deleted=True)
        with patch("app.services.clients.delete_client", return_value=fake) as mock_service:
            resp = client.delete("/clients/1")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(mock_db, 1)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.delete("/clients/1")
        assert resp.status_code in (401, 403)


class TestUploadLogo:

    def test_success(self, client, mock_db):
        with patch("app.services.clients.upload_company_logo") as mock_service:
            mock_service.return_value = _fake_client(company_logo_url="http://s3/logo.png")
            
            files = {"file": ("logo.png", b"fake-image-content", "image/png")}
            resp = client.post("/clients/1/logo", files=files)
            
        assert resp.status_code == 200
        assert resp.json()["company_logo_url"] == "http://s3/logo.png"
        mock_service.assert_called_once()

    def test_unauthenticated(self, unauth_client):
        files = {"file": ("logo.png", b"content", "image/png")}
        resp = unauth_client.post("/clients/1/logo", files=files)
        assert resp.status_code in (401, 403)


class TestBulkApproveClients:

    def test_success(self, client, mock_db):
        payload = {"client_ids": [1, 2], "action": "approve"}
        with patch("app.routes.clients.require_admin", return_value=True):
            with patch("app.services.clients.bulk_update_client_status") as mock_service:
                mock_service.return_value = [_fake_client(client_id=1), _fake_client(client_id=2)]
                resp = client.patch("/clients/bulk-approve", json=payload)
        
        assert resp.status_code == 200
        assert len(resp.json()) == 2
        mock_service.assert_called_once_with(db=mock_db, client_ids=[1, 2], action="approve")

    def test_non_admin_forbidden(self, regular_client):
        payload = {"client_ids": [1, 2], "action": "approve"}
        with patch("app.routes.clients.require_admin", side_effect=HTTPException(status_code=403)):
            resp = regular_client.patch("/clients/bulk-approve", json=payload)
        assert resp.status_code == 403
