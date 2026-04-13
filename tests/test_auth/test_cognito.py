import pytest
from unittest.mock import MagicMock, patch
from app.auth.cognito import get_jwks, _fetch_jwks, _reset_jwks_cache

@pytest.fixture(autouse=True)
def reset_jwks():
    _reset_jwks_cache()


@patch("app.auth.cognito.requests.get")
def test_fetch_jwks_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"keys": [{"kid": "123", "alg": "RS256"}]}
    mock_get.return_value = mock_response

    keys = _fetch_jwks()
    assert len(keys) == 1
    assert keys[0]["kid"] == "123"

@patch("app.auth.cognito.requests.get")
def test_fetch_jwks_invalid_payload(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"invalid": "payload"}
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Invalid JWKS payload"):
        _fetch_jwks()

@patch("app.auth.cognito._fetch_jwks")
def test_get_jwks_caching(mock_fetch):
    mock_fetch.return_value = [{"kid": "123"}]
    
    # First call - should fetch
    keys1 = get_jwks(force_refresh=True)
    assert keys1 == [{"kid": "123"}]
    assert mock_fetch.call_count == 1

    # Second call - should return from cache
    keys2 = get_jwks()
    assert keys2 == [{"kid": "123"}]
    assert mock_fetch.call_count == 1 # Still 1

@patch("app.auth.cognito._fetch_jwks")
def test_get_jwks_force_refresh(mock_fetch):
    mock_fetch.return_value = [{"kid": "123"}]
    get_jwks()
    
    # Force refresh
    get_jwks(force_refresh=True)
    assert mock_fetch.call_count == 2
