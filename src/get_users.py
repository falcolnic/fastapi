from src import models
from src.database import Base, engine, SessionLocal, get_db


from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from src.auth_bearer import JWTBearer

        
router=APIRouter(
    prefix='/admin',
    tags=['info']
)

    
@router.get('/getusers')
def getusers(dependencies=Depends(JWTBearer()), session: Session = Depends(get_db)):
    user = session.query(models.User).all()
    return user



    
    
