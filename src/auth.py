# Package
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy import func
# Local
import src.schemas as schemas
import src.models as models
from src.database import Base, engine, SessionLocal, get_db
from src.utils import create_access_token,create_refresh_token,verify_password,get_hashed_password
from src.otp import generate_OTP

# Env
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

        
        
router=APIRouter(
    prefix='/auth',
    tags=['auth']
)


#Working
@router.post("/register")
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter_by(email=user.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    encrypted_password = get_hashed_password(user.password)
    user.password = encrypted_password
    
    otp = generate_OTP()
    otp_expiry = datetime.now() + timedelta(minutes=5)
    
    new_user = models.User(
        username=user.username,
        email=user.email.lower(),
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
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    await fm.send_message(message)
    return {"message":"Registration successful, check your email for OTP code for login"}


@router.post('/login', response_model=schemas.TokenSchema)
def login(request: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(func.lower(models.User.email) == request.email.lower()).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    
    hashed_pass = user.password
    
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
        
    # Verify OTP
    if request.otp != user.otp or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
        
    # Generate tokens
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
    