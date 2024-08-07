from datetime import datetime, timedelta
import schemas
import models
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Request, status, APIRouter
from utils import get_hashed_password
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from otp import generate_OTP

import os
from dotenv import load_dotenv
load_dotenv('.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
router=APIRouter(
    prefix='/auth',
    tags=['auth-in']
)


#Working
@router.post("/register")
async def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    encrypted_password = get_hashed_password(user.password)
    user.password = encrypted_password
    
    otp = generate_OTP()
    otp_expiry = datetime.now() + timedelta(minutes=5)
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=encrypted_password,
        otp=otp,
        otp_expiry=otp_expiry
    )
    
    html = f"<p>Thank you for choosing us, here is your OTP Code: {otp} for this Username: {user.username}</p>"
    message = MessageSchema(
            subject="Verification Code",
            recipients=[user.email],
            body=html,
            subtype=MessageType.html)
    fm = FastMail(conf)
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    await fm.send_message(message)
    return {"message":"user and mail successfully"}


