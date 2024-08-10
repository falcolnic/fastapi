# Packages
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import  HTTPException, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# conf
import os
from dotenv import load_dotenv
load_dotenv('.env')
class Envs:
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGO = os.getenv('ALGO')
    REFRESH_SECRET = os.getenv('REFRESH_SECRET')
    
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 days
ALGORITHM = Envs.ALGO
JWT_SECRET_KEY = Envs.SECRET_KEY # changed the secret key
JWT_REFRESH_SECRET_KEY = Envs.REFRESH_SECRET

def decodeJWT(jwtoken: str):
    try:
        # Decode and verify the token
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid

jwt_bearer = JWTBearer()