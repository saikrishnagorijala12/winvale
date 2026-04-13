import pytest
from unittest.mock import MagicMock, patch
from app.services.clients import (
    get_client_by_id,
    update_client_status,
    bulk_update_client_status,
    delete_client,
    ClientNotFoundError,
)
from app.models.client_profiles import ClientProfile
from app.models.status import Status

@pytest.fixture
def mock_db():
    return MagicMock()

def test_get_client_by_id_found(mock_db):
    client = MagicMock(spec=ClientProfile)
    client.client_id = 1
    client.contracts = None
    client.negotiators = []
    client.status = MagicMock()
    client.status.status = "pending"
    mock_db.query().filter().first.return_value = client

    with patch("app.services.clients.serialize_client") as mock_serialize:
        get_client_by_id(mock_db, 1)
        mock_serialize.assert_called_once_with(client)

def test_get_client_by_id_not_found(mock_db):
    mock_db.query().filter().first.return_value = None
    result = get_client_by_id(mock_db, 999)
    assert result is None

def test_update_client_status_approve(mock_db):
    client = MagicMock(spec=ClientProfile)
    client.client_id = 1
    client.status_id = 1 # pending
    mock_db.query().filter().first.return_value = client

    with patch("app.services.clients.get_status_id_by_name", return_value=2): # 2 = approved
        with patch("app.services.clients.serialize_client"):
            update_client_status(mock_db, client_id=1, action="approve")
            assert client.status_id == 2
            mock_db.commit.assert_called_once()

def test_update_client_status_not_found(mock_db):
    mock_db.query().filter().first.return_value = None
    with pytest.raises(ClientNotFoundError):
        update_client_status(mock_db, client_id=999, action="approve")

def test_delete_client(mock_db):
    client = MagicMock(spec=ClientProfile)
    client.client_id = 1
    client.is_deleted = False
    mock_db.query().filter().first.return_value = client

    with patch("app.services.clients.serialize_client"):
        delete_client(mock_db, 1)
        assert client.is_deleted is True
        mock_db.commit.assert_called_once()
