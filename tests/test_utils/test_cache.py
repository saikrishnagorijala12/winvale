import pytest
import json
from unittest.mock import MagicMock, patch
from redis.exceptions import RedisError
from app.utils.cache import (
    cache_get_or_set,
    invalidate_keys,
    invalidate_pattern,
    clear_all_cache,
    _is_empty_result,
    _reset_redis_backoff
)

@pytest.fixture(autouse=True)
def reset_backoff():
    _reset_redis_backoff()

@pytest.fixture
def mock_redis():
    return MagicMock()

def test_is_empty_result():
    assert _is_empty_result(None) is True
    assert _is_empty_result([]) is True
    assert _is_empty_result({"total": 0, "items": []}) is True
    assert _is_empty_result([1, 2, 3]) is False
    assert _is_empty_result({"total": 1, "items": [1]}) is False
    assert _is_empty_result("some string") is False

def test_cache_get_or_set_hit(mock_redis):
    key = "test_key"
    cached_data = {"foo": "bar"}
    mock_redis.get.return_value = json.dumps(cached_data)
    fetch_fn = MagicMock()

    result = cache_get_or_set(mock_redis, key, 300, fetch_fn)

    assert result == cached_data
    mock_redis.get.assert_called_once_with(key)
    fetch_fn.assert_not_called()

def test_cache_get_or_set_miss(mock_redis):
    key = "test_key"
    fresh_data = {"foo": "bar"}
    mock_redis.get.return_value = None
    fetch_fn = MagicMock(return_value=fresh_data)

    result = cache_get_or_set(mock_redis, key, 300, fetch_fn)

    assert result == fresh_data
    mock_redis.get.assert_called_once_with(key)
    fetch_fn.assert_called_once()
    mock_redis.setex.assert_called_once()

def test_cache_get_or_set_redis_error(mock_redis):
    key = "test_key"
    fresh_data = {"foo": "bar"}
    mock_redis.get.side_effect = RedisError("Connection failed")
    fetch_fn = MagicMock(return_value=fresh_data)

    # We need to make sure we don't persist the disabled state across tests
    with patch("app.utils.cache._redis_temporarily_disabled", return_value=False):
        result = cache_get_or_set(mock_redis, key, 300, fetch_fn)

    assert result == fresh_data
    fetch_fn.assert_called_once()

def test_invalidate_keys(mock_redis):
    invalidate_keys(mock_redis, "key1", "key2")
    assert mock_redis.delete.call_count == 2
    mock_redis.delete.assert_any_call("key1")
    mock_redis.delete.assert_any_call("key2")

def test_invalidate_pattern(mock_redis):
    mock_redis.scan_iter.return_value = ["key:1", "key:2"]
    count = invalidate_pattern(mock_redis, "key:*")
    assert count == 2
    assert mock_redis.delete.call_count == 2
    mock_redis.scan_iter.assert_called_once_with(match="key:*")

def test_clear_all_cache(mock_redis):
    clear_all_cache(mock_redis)
    mock_redis.flushdb.assert_called_once()
