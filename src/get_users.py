from src import models
from src.database import Base, engine, SessionLocal


from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from src.auth_bearer import JWTBearer


Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
router=APIRouter(
    prefix='/admin',
    tags=['info']
)

    
@router.get('/getusers')
def getusers(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    user = session.query(models.User).all()
    return user



    
    
