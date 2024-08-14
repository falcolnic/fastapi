from sqlalchemy.orm import Session
from src import models
import schemas as schemas
from sqlalchemy.exc import IntegrityError
from src.utils import create_access_token,create_refresh_token,verify_password,get_hashed_password
from sqlalchemy import func, desc
from fastapi import Depends
from src.otp import generate_OTP
from datetime import datetime, timedelta


class DuplicateError(Exception):
    pass


def add_user(user: schemas.UserCreate, db: Session, provider: str = None):
    
    if not provider and not user.password:
        raise ValueError("A password should be provided for non SSO registers")
    elif provider and user.password:
        raise ValueError("A password should not be provided for SSO registers")
    
    encrypted_password = get_hashed_password(user.password)
    user.password = encrypted_password
    
    otp = generate_OTP()
    otp_expiry = datetime.now() + timedelta(minutes=5)
    
    new_user = models.User(
            username=user.username,
            email=user.email.lower(),
            password=encrypted_password,
            otp=otp,
            otp_expiry=otp_expiry,
            provider=provider
        )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise DuplicateError(
            f"Username {user.username} is already attached to a "
            "registered user for the provider '{provider}'."
        )
    return user


def get_user(db: Session, username: str, provider: str):
    user = db.query(models.User).filter(models.User.username == username).filter(
        models.User.provider == provider).first()
    return user