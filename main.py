from contextlib import asynccontextmanager
from auth import *
from fastapi import FastAPI, APIRouter



@asynccontextmanager
async def get_app():
    app = FastAPI()
    router = APIRouter()
    app.include_router(router)
    yield app
    
