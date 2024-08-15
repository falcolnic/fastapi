from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter

from src.utils import verify_password,get_hashed_password
import src.schemas as schemas
import src.models as models
from src.database import Base, engine, SessionLocal, get_db
from src.auth_bearer import JWTBearer
        
router=APIRouter(tags=['User Management'])

@router.get('/getusers')
def getusers(dependencies=Depends(JWTBearer()), session: Session = Depends(get_db)):
    user = session.query(models.User).all()
    return user

@router.post('/change-password')
def change_password(request: schemas.changepassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
    
    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.delete('/deleteuser/{id}')
def delete_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}