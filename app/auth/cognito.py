import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

AWS_REGION = "ap-south-1"        # change if needed
USER_POOL_ID = "ap-south-1_XXXX" # your user pool id
APP_CLIENT_ID = "XXXXXXXX"       # your app client id

COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()["keys"]
