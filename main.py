from fastapi import FastAPI, APIRouter
from auth import router as auth_router
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager



router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@asynccontextmanager
async def get_app():
    app = FastAPI()
    app.include_router(auth_router)
    yield app
    
app = FastAPI()
app.include_router(auth_router)