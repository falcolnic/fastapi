from fastapi import FastAPI, APIRouter
from auth import router as auth_router
from otp import router as otp_router
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager



router = APIRouter()



app = FastAPI()
app.include_router(auth_router)
app.include_router(otp_router)