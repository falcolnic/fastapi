from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, APIRouter

 
app = FastAPI()
router = APIRouter()




class User(BaseModel):
    username: str
    mail: str
    phone: str
    password: str

@router.post("/register", tags=["auth"], status_code=200)
async def register(user: User):
    return "User, " + user.username + " with " + user.mail + " registered"
    


@router.post("/login", tags=["auth"], status_code=200)
async def login(user: User):
    return "User, " + user.username + " loggwed in"



app.include_router(router)