import requests

from app.config import settings

AWS_REGION = settings.AWS_REGION
USER_POOL_ID = settings.USER_POOL_ID
APP_CLIENT_ID = settings.APP_CLIENT_ID
 
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

 
jwks = requests.get(JWKS_URL).json()["keys"]