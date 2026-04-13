

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Build a mock Redis client whose .get() always returns None (cache miss).
# This means every cache_get_or_set call will delegate to fetch_fn().
# ---------------------------------------------------------------------------
_mock_redis = MagicMock()
_mock_redis.get.return_value = None
_mock_redis.setex.return_value = True
_mock_redis.delete.return_value = True
_mock_redis.scan_iter.return_value = iter([])


with patch("app.auth.cognito.requests") as _mock_req:
    _mock_req.get.return_value.json.return_value = {"keys": []}
    with patch("app.redis_client.redis", MagicMock()):
        with patch("app.redis_client.redis_client", _mock_redis):
            from main import app  

from app.auth.dependencies import get_current_user  
from app.database import get_db  


FAKE_ADMIN_USER = {
    "name": "Admin User",
    "email": "admin@test.com",
    "sub": "admin-cognito-sub-001",
    "groups": ["admin"],
}

FAKE_REGULAR_USER = {
    "name": "Regular User",
    "email": "user@test.com",
    "sub": "user-cognito-sub-002",
    "groups": [],
}


@pytest.fixture()
def mock_db():
    """Return a MagicMock that stands in for a SQLAlchemy Session."""
    return MagicMock()



@pytest.fixture(autouse=True)
def _reset_redis_mock():
    """
    Before each test, reset the mock redis client so .get() returns None
    (cache miss).  This ensures every route delegates to its real fetch_fn.
    """
    _mock_redis.reset_mock()
    _mock_redis.get.return_value = None
    _mock_redis.setex.return_value = True
    _mock_redis.delete.return_value = True
    _mock_redis.scan_iter.return_value = iter([])
    yield


@pytest.fixture()
def client(mock_db):
    """
    TestClient whose requests look like they come from an admin user.
    `get_db` yields the mock_db fixture so service-layer patches work.
    """
    def _override_current_user():
        return FAKE_ADMIN_USER

    def _override_get_db():
        yield mock_db

    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def regular_client(mock_db):
    """TestClient whose requests come from a non-admin user."""
    def _override_current_user():
        return FAKE_REGULAR_USER

    def _override_get_db():
        yield mock_db

    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def unauth_client(mock_db):
    """
    TestClient with NO auth override → `get_current_user` runs normally
    and will reject because there is no valid Cognito JWT.
    """
    def _override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
