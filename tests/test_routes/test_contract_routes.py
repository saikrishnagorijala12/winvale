import pytest
from unittest.mock import patch, ANY
from fastapi import status
from tests.conftest import FAKE_ADMIN_USER
from datetime import datetime, timezone


NOW = datetime.now(timezone.utc).isoformat()


def _fake_contract(**overrides):
    base = {
        "client_id": 1,
        "client": "Acme Corp",
        "contract_number": "GS-35F-0001",
        "contract_officer_name": "John Doe",
        "contract_officer_address": "456 Oak Ave",
        "contract_officer_city": "Washington",
        "contract_officer_state": "DC",
        "contract_officer_zip": "20001",
        "origin_country": "US",
        "gsa_proposed_discount": 15.5,
        "q_v_discount": "5%",
        "additional_concessions": "None",
        "normal_delivery_time": 30,
        "expedited_delivery_time": 10,
        "fob_term": "Destination",
        "energy_star_compliance": "Yes",
        "is_deleted": False,
        "created_time": NOW,
        "updated_time": NOW,
    }
    base.update(overrides)
    return base


VALID_CONTRACT_PAYLOAD = {
    "contract_number": "GS-35F-0001",
    "contract_officer_name": "John Doe",
    "contract_officer_address": "456 Oak Ave",
    "contract_officer_city": "Washington",
    "contract_officer_state": "DC",
    "contract_officer_zip": "20001",
    "origin_country": "US",
    "gsa_proposed_discount": 15.5,
    "normal_delivery_time": 30,
    "expedited_delivery_time": 10,
    "fob_term": "Destination",
    "energy_star_compliance": "Yes",
}


class TestGetAllContracts:

    def test_success(self, client, mock_db):
        with patch(
            "app.services.contracts.get_all_client_contracts",
            return_value=[_fake_contract()],
        ) as mock_service:
            resp = client.get("/contracts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert resp.json()[0]["contract_number"] == "GS-35F-0001"
        mock_service.assert_called_once_with(mock_db)

    def test_empty_list(self, client):
        with patch("app.services.contracts.get_all_client_contracts", return_value=[]) as mock_service:
            resp = client.get("/contracts")
        assert resp.status_code == 200
        assert resp.json() == []
        mock_service.assert_called_once()

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/contracts")
        assert resp.status_code in (401, 403)


class TestGetContractByClientId:

    def test_success(self, client, mock_db):
        fake = _fake_contract(client_id=10)
        with patch("app.services.contracts.get_contract_by_client_id", return_value=fake) as mock_service:
            resp = client.get("/contracts/10")
        assert resp.status_code == 200
        assert resp.json()["client_id"] == 10
        mock_service.assert_called_once_with(mock_db, 10)

    def test_not_found(self, client, mock_db):
        with patch("app.services.contracts.get_contract_by_client_id", return_value=None) as mock_service:
            resp = client.get("/contracts/999")
        assert resp.status_code == 404
        mock_service.assert_called_once_with(mock_db, 999)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/contracts/1")
        assert resp.status_code in (401, 403)


class TestCreateContract:

    def test_success(self, client, mock_db):
        fake = _fake_contract(client_id=5)
        with patch("app.services.contracts.create_contract_by_client_id", return_value=fake) as mock_service:
            resp = client.post("/contracts/5", json=VALID_CONTRACT_PAYLOAD)
        assert resp.status_code == 200
        mock_service.assert_called_once_with(db=mock_db, client_id=5, payload=ANY)

    def test_conflict(self, client, mock_db):
        from app.services.contracts import ContractAlreadyExsistsError

        with patch(
            "app.services.contracts.create_contract_by_client_id",
            side_effect=ContractAlreadyExsistsError(),
        ) as mock_service:
            resp = client.post("/contracts/5", json=VALID_CONTRACT_PAYLOAD)
        assert resp.status_code == 409
        mock_service.assert_called_once_with(db=mock_db, client_id=5, payload=ANY)

    def test_validation_missing_contract_number(self, client):
        bad = {**VALID_CONTRACT_PAYLOAD}
        del bad["contract_number"]
        resp = client.post("/contracts/5", json=bad)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_validation_empty_body(self, client):
        resp = client.post("/contracts/5", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post("/contracts/5", json=VALID_CONTRACT_PAYLOAD)
        assert resp.status_code in (401, 403)


class TestUpdateContract:

    def test_success(self, client, mock_db):
        fake = _fake_contract(client_id=5)
        with patch("app.services.contracts.update_contract_by_client_id", return_value=fake) as mock_service:
            resp = client.put("/contracts/5", json=VALID_CONTRACT_PAYLOAD)
        assert resp.status_code == 200
        mock_service.assert_called_once_with(db=mock_db, client_id=5, payload=ANY)

    def test_not_found(self, client, mock_db):
        with patch("app.services.contracts.update_contract_by_client_id", return_value=None) as mock_service:
            resp = client.put("/contracts/999", json=VALID_CONTRACT_PAYLOAD)
        assert resp.status_code == 404
        mock_service.assert_called_once_with(db=mock_db, client_id=999, payload=ANY)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.put("/contracts/1", json={"contract_number": "X"})
        assert resp.status_code in (401, 403)


class TestDeleteContract:

    def test_success(self, client, mock_db):
        fake = _fake_contract(is_deleted=True)
        with patch("app.services.contracts.delete_contract", return_value=fake) as mock_service:
            resp = client.delete("/contracts/5")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(mock_db, 5)

    def test_not_found(self, client, mock_db):
        from app.services.contracts import ClientNotFoundError

        with patch(
            "app.services.contracts.delete_contract",
            side_effect=ClientNotFoundError(),
        ) as mock_service:
            resp = client.delete("/contracts/999")
        assert resp.status_code == 404
        mock_service.assert_called_once_with(mock_db, 999)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.delete("/contracts/1")
        assert resp.status_code in (401, 403)
