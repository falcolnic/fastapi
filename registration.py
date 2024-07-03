from datetime import datetime
import random
import schemas
import models
from models import TokenTable, User
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Request, status, APIRouter
import jwt
from auth_bearer import JWTBearer
from utils import create_access_token,create_refresh_token,verify_password,get_hashed_password
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List

#ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
#REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
#ALGORITHM = "HS256"
#JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"   # should be kept secret
#JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"


Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
router=APIRouter()


# @router.post("/register")
# def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
#     existing_user = session.query(models.User).filter_by(email=user.email).first()
#     if existing_user != None:
#         raise HTTPException(
#             detail='Email is already registered',
#             status_code= status.HTTP_409_CONFLICT
#         )

#     encrypted_password = get_hashed_password(user.password)
#     user.password = encrypted_password
    
#     new_user = models.User(username=user.username, email=user.email, password=encrypted_password )
    
#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)
    
#     return {"message":"user created successfully"}


# @router.post('/register/',status_code= status.HTTP_201_CREATED, response_model=schemas.RegistrationUserRepsonse)
# async def register(request:Request,user_credentials:schemas.UserCreate,  db: Session = Depends(get_session)):
#     email_check = db.query(models.User).filter(models.User.email ==user_credentials.email).first()
#     if email_check !=None:
#        raise HTTPException(
#         detail='Email is already registered',
#         status_code= status.HTTP_409_CONFLICT
#        )
       
#     hashed_password = get_hashed_password(user_credentials.password)
#     user_credentials.password = hashed_password
    
#     new_user = models.User(email = user_credentials.email,
#     password = user_credentials.password)
    
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     db.commit()
#     return {
#     "message": "User registration successful",
#     "data": new_user
#     }