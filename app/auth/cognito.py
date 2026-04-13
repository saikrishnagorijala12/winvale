import time
from typing import Any

import requests

from app.config import settings

AWS_REGION = settings.AWS_REGION
USER_POOL_ID = settings.USER_POOL_ID
APP_CLIENT_ID = settings.APP_CLIENT_ID

COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

_jwks_cache: list[dict[str, Any]] | None = None
_jwks_cache_until = 0.0
_jwks_retry_after = 0.0


def _reset_jwks_cache():
    global _jwks_cache, _jwks_cache_until, _jwks_retry_after
    _jwks_cache = None
    _jwks_cache_until = 0.0
    _jwks_retry_after = 0.0


def _fetch_jwks() -> list[dict[str, Any]]:
    response = requests.get(
        JWKS_URL,
        timeout=settings.COGNITO_JWKS_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()

    keys = payload.get("keys")
    if not isinstance(keys, list) or not keys:
        raise ValueError("Invalid JWKS payload")

    return keys


def get_jwks(force_refresh: bool = False) -> list[dict[str, Any]]:
    global _jwks_cache, _jwks_cache_until, _jwks_retry_after

    now = time.monotonic()

    if not force_refresh and _jwks_cache and now < _jwks_cache_until:
        return _jwks_cache

    if not force_refresh and now < _jwks_retry_after and _jwks_cache:
        return _jwks_cache

    try:
        keys = _fetch_jwks()
        _jwks_cache = keys
        _jwks_cache_until = now + settings.COGNITO_JWKS_CACHE_SECONDS
        _jwks_retry_after = 0.0
        return keys
    except Exception:
        _jwks_retry_after = now + settings.COGNITO_JWKS_RETRY_BACKOFF_SECONDS
        if _jwks_cache:
            return _jwks_cache
        raise
