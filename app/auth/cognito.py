import requests
from jose import jwk, jwt
from jose.utils import base64url_decode
import os, dotenv
 
dotenv.load_dotenv()
 
AWS_REGION = os.getenv('AWS_REGION')
USER_POOL_ID = os.getenv('USER_POOL_ID')
APP_CLIENT_ID = os.getenv('APP_CLIENT_ID')
 
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

 
jwks = requests.get(JWKS_URL).json()["keys"]
 