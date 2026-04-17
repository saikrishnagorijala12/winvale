import logging
from time import perf_counter

from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

from app.auth.cognito import APP_CLIENT_ID, COGNITO_ISSUER, get_jwks

security = HTTPBearer()
logger = logging.getLogger("app.auth")


def get_current_user(
    token: Optional[str] = Query(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    actual_token = token if token else (credentials.credentials if credentials else None)
    if not actual_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    start = perf_counter()
    try:
        header = jwt.get_unverified_header(actual_token)
        kid = header["kid"]
        keys = get_jwks()
        key = next((k for k in keys if k.get("kid") == kid), None)
        # Keys can rotate; retry once with a forced refresh.
        if key is None:
            keys = get_jwks(force_refresh=True)
            key = next(k for k in keys if k.get("kid") == kid)

        claims = jwt.decode(
            actual_token,
            key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=COGNITO_ISSUER
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    return {
        "name": claims.get("name"),
        "email": claims.get("email"),
        "sub": claims.get("sub"),
        "groups": claims.get("cognito:groups", [])
    }
