from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from src import models
from sqlalchemy import func
from sqlalchemy.orm import Session

# conf
import os
from dotenv import load_dotenv
load_dotenv('A:\\soloFAST\\src\\.env')

class Envs:
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGO = os.getenv('ALGO')
    REFRESH_SECRET = os.getenv('REFRESH_SECRET')

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 days
ALGORITHM = Envs.ALGO
JWT_SECRET_KEY = Envs.SECRET_KEY # changed the secret key
JWT_REFRESH_SECRET_KEY = Envs.REFRESH_SECRET


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    if password is None:
        return None
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
        
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
         
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
     
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str, provider: str):
    user = db.query(models.User).filter(func.lower(models.User.email) == email.lower()).filter(models.User.provider == provider).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user