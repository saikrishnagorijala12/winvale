import logging
from time import perf_counter

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

from app.auth.cognito import APP_CLIENT_ID, COGNITO_ISSUER, get_jwks

security = HTTPBearer()
logger = logging.getLogger("app.auth")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    start = perf_counter()
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        keys = get_jwks()
        key = next((k for k in keys if k.get("kid") == kid), None)

        # Keys can rotate; retry once with a forced refresh.
        if key is None:
            keys = get_jwks(force_refresh=True)
            key = next(k for k in keys if k.get("kid") == kid)

        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=COGNITO_ISSUER
        )

    except Exception:
        duration_ms = round((perf_counter() - start) * 1000, 2)
        logger.warning("token_validation_failed duration_ms=%s", duration_ms)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    duration_ms = round((perf_counter() - start) * 1000, 2)
    logger.info(
        "token_validation_complete email=%s duration_ms=%s",
        claims.get("email"),
        duration_ms,
    )
    return {
        "name": claims.get("name"),
        "email": claims.get("email"),
        "sub": claims.get("sub"),
        "groups": claims.get("cognito:groups", [])
    }
