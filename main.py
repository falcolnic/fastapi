from fastapi import FastAPI, APIRouter

from login import router as login_router
from registration import router as registration_router
from logout import router as logout_router
from otp import router as otp_router

from contextlib import asynccontextmanager



app = FastAPI()
app.include_router(login_router)
app.include_router(registration_router)
app.include_router(logout_router)

app.include_router(otp_router)