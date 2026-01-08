from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from app.auth.cognito import jwks, COGNITO_ISSUER, APP_CLIENT_ID

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        key = next(k for k in jwks if k["kid"] == kid)

        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=COGNITO_ISSUER
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return {
        "name" : claims.get("name"),
        "email": claims.get("email"),
        "sub": claims.get("sub"),
        "groups": claims.get("cognito:groups", [])
    }


