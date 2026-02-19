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


def cache_get_or_set(
    redis_client: Redis,
    key: str,
    ttl: int,
    fetch_fn: Callable[[], Any],
) -> Any:
    """
    Return cached value for *key* if present, otherwise call *fetch_fn*,
    store the result in Redis with the given *ttl* (seconds), and return it.
    """
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    data = fetch_fn()
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
