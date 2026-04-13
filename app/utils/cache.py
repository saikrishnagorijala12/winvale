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
import logging
import time
from typing import Callable, Any

from fastapi.encoders import jsonable_encoder
from redis import Redis
from redis.exceptions import RedisError

from app.config import settings


_redis_disabled_until = 0.0
logger = logging.getLogger("app.cache")


def _disable_redis_temporarily() -> None:
    global _redis_disabled_until
    _redis_disabled_until = time.monotonic() + settings.REDIS_FAILURE_BACKOFF_SECONDS


def _reset_redis_backoff() -> None:
    global _redis_disabled_until
    _redis_disabled_until = 0.0


def _redis_temporarily_disabled() -> bool:
    return time.monotonic() < _redis_disabled_until


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

    If Redis is unavailable, this degrades gracefully to direct fetches.
    """
    if _redis_temporarily_disabled():
        fetch_start = time.perf_counter()
        data = fetch_fn()
        fetch_duration_ms = round((time.perf_counter() - fetch_start) * 1000, 2)
        logger.info(
            "cache_bypassed_redis_disabled key=%s fetch_duration_ms=%s",
            key,
            fetch_duration_ms,
        )
        return data

    redis_start = time.perf_counter()
    try:
        cached = redis_client.get(key)
        redis_duration_ms = round((time.perf_counter() - redis_start) * 1000, 2)
        if cached:
            logger.info(
                "cache_hit key=%s redis_duration_ms=%s",
                key,
                redis_duration_ms,
            )
            return json.loads(cached)
    except RedisError:
        _disable_redis_temporarily()
        fetch_start = time.perf_counter()
        data = fetch_fn()
        fetch_duration_ms = round((time.perf_counter() - fetch_start) * 1000, 2)
        logger.warning(
            "cache_redis_get_failed key=%s fetch_duration_ms=%s",
            key,
            fetch_duration_ms,
        )
        return data

    fetch_start = time.perf_counter()
    data = fetch_fn()
    fetch_duration_ms = round((time.perf_counter() - fetch_start) * 1000, 2)
    logger.info(
        "cache_miss key=%s fetch_duration_ms=%s",
        key,
        fetch_duration_ms,
    )

    if not _is_empty_result(data):
        try:
            redis_set_start = time.perf_counter()
            redis_client.setex(key, ttl, json.dumps(jsonable_encoder(data)))
            redis_set_duration_ms = round((time.perf_counter() - redis_set_start) * 1000, 2)
            logger.info(
                "cache_store key=%s redis_duration_ms=%s",
                key,
                redis_set_duration_ms,
            )
        except RedisError:
            _disable_redis_temporarily()
            logger.warning("cache_store_failed key=%s", key)

    return data


def invalidate_keys(redis_client: Redis, *keys: str) -> None:
    """
    Delete one or more exact cache keys from Redis.
    Pass as many keys as needed, e.g.:
        invalidate_keys(redis_client, "clients:all", f"clients:id:{client_id}")
    """
    if _redis_temporarily_disabled():
        return

    for key in keys:
        try:
            redis_client.delete(key)
        except RedisError:
            _disable_redis_temporarily()
            return


def invalidate_pattern(redis_client: Redis, pattern: str) -> int:
    """
    Invalidate all keys matching the given pattern using SCAN.
    Returns the number of keys deleted.
    """
    if _redis_temporarily_disabled():
        return 0

    count = 0
    try:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            count += 1
    except RedisError:
        _disable_redis_temporarily()
        return count

    return count


def clear_all_cache(redis_client: Redis) -> None:
    """
    Best-effort global cache clear used by mutate middleware.
    """
    if _redis_temporarily_disabled():
        return

    try:
        redis_client.flushdb()
    except RedisError:
        _disable_redis_temporarily()
