"""
Shared Redis cache helpers.

Usage:
    from app.utils.cache import cache_get_or_set, invalidate_keys
    from app.redis_client import redis_client

    # Cache-aside read
    data = cache_get_or_set(redis_client, "my:key", 300, lambda: fetch_from_db())

    # Invalidate on write
    invalidate_keys(redis_client, "my:key", "other:key")
"""

import json
from typing import Callable, Any

from fastapi.encoders import jsonable_encoder
from redis import Redis


def _is_empty_result(data: Any) -> bool:
    """
    Return True if *data* represents an empty result that should NOT be cached.
    Covers:
    - Empty lists:  []
    - Paginated responses where total == 0:  {"total": 0, "items": [...]}
    - None / falsy scalars
    """
    if data is None:
        return True
    if isinstance(data, list) and len(data) == 0:
        return True
    if isinstance(data, dict):
        # Paginated response shape
        if "total" in data and data["total"] == 0:
            return True
    return False


def cache_get_or_set(
    redis_client: Redis,
    key: str,
    ttl: int,
    fetch_fn: Callable[[], Any],
) -> Any:
    """
    Return cached value for *key* if present, otherwise call *fetch_fn*,
    store the result in Redis with the given *ttl* (seconds), and return it.

    Empty results (empty list or paginated response with total=0) are never
    cached so that a transient empty DB state doesn't get locked in.
    """
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    data = fetch_fn()

    if not _is_empty_result(data):
        redis_client.setex(key, ttl, json.dumps(jsonable_encoder(data)))

    return data


def invalidate_keys(redis_client: Redis, *keys: str) -> None:
    """
    Delete one or more exact cache keys from Redis.
    Pass as many keys as needed, e.g.:
        invalidate_keys(redis_client, "clients:all", f"clients:id:{client_id}")
    """
    for key in keys:
        redis_client.delete(key)


def invalidate_pattern(redis_client: Redis, pattern: str) -> int:
    """
    Invalidate all keys matching the given pattern using SCAN.
    Returns the number of keys deleted.
    """
    count = 0
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
        count += 1
    return count
