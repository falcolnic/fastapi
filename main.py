from fastapi import FastAPI, APIRouter
import uvicorn
from contextlib import asynccontextmanager

from src.login import router as login_router
from src.registration import router as registration_router
from src.logout import router as logout_router

app = FastAPI()
app.include_router(login_router)
app.include_router(registration_router)
app.include_router(logout_router)

     
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)