from datetime import datetime
import random
import schemas
import models
from models import TokenTable, User
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
import jwt
from auth_bearer import JWTBearer
from utils import create_access_token,create_refresh_token,verify_password,get_hashed_password
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List


Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
router=APIRouter()

    
@router.get('/getusers')
def getusers(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    user = session.query(models.User).all()
    return user



@router.post('/login' ,response_model=schemas.TokenSchema)
def login(request: schemas.UserLogin, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    
    hashed_pass = user.password
    
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
        
    access=create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = models.TokenTable(user_id=user.id,  access_toke=access,  refresh_toke=refresh, status=True)
    
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
   
   
    return {
        "access_token": access,
        "refresh_token": refresh,
    }
    
    
    
    
    
    
# @router.post('/login' ,response_model=schemas.TokenSchema)
# def login(request: schemas.UserLogin, db: Session = Depends(get_session)):
#     user = db.query(User).filter(User.email == request.email).first()
    
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    
#     hashed_pass = user.password
    
#     if not verify_password(request.password, hashed_pass):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Incorrect password"
#         )
        
#     access=create_access_token(user.id)
#     refresh = create_refresh_token(user.id)

#     token_db = models.TokenTable(user_id=user.id,  access_toke=access,  refresh_toke=refresh, status=True)
    
#     db.add(token_db)
#     db.commit()
#     db.refresh(token_db)
   
#     return {
#         "access_token": access,
#         "refresh_token": refresh,
#     }
    