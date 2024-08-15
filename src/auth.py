# Package
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy import func
# Local
from src.auth_bearer import ALGORITHM, JWT_SECRET_KEY, JWTBearer
from src import db_crud
import src.schemas as schemas
import src.models as models
from src.database import get_db
from src.utils import create_access_token,create_refresh_token,verify_password,get_hashed_password

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

router=APIRouter(prefix='/v1')

#Working
@router.post("/register", response_model=schemas.User, tags=['Auth'])
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db), provider: str = None):
    existing_user = db.query(models.User).filter_by(email=user.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    existing_user_provider = db.query(models.User).filter_by(username=user.username, provider=provider).first()
    if existing_user_provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username {user.username} is already attached to a registered user for the provider '{provider}'.")
    
    if provider:
        user.password = None
        
    new_user = db_crud.add_user(user, db, provider)
    
    if not provider:
        html = f"<p>Thank you for choosing us, here is your OTP Code: {db_crud.otp} for this Username: {user.username}</p>"
        message = MessageSchema(
                subject="Verification Code",
                recipients=[user.email],
                body=html,
                subtype=MessageType.html)
        fm = FastMail(conf)
        await fm.send_message(message)
        
    # Exclude provider from the response
    response_user = schemas.User(
        email=new_user.email,
        password=new_user.password,
        provider=None
    )
    return response_user


@router.post('/login', response_model=schemas.TokenSchema, tags=['Auth'])
def login(request: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(func.lower(models.User.email) == request.email.lower()).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    
    hashed_pass = user.password
    
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password or mail"
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
    
@router.post('/logout', tags=['Auth'])
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    token=dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_record = db.query(models.TokenTable).all()
    info=[]
    for record in token_record :
        print("record",record)
        if (datetime.utcnow() - record.created_date).days >1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(models.TokenTable).where(models.TokenTable.user_id.in_(info)).delete()
        db.commit()
        
    existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id, models.TokenTable.access_toke==token).first()
    if existing_token:
        existing_token.status=False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message":"Logout Successfully"} 