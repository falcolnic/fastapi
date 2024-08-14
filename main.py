import asyncio
from fastapi import FastAPI, APIRouter
import uvicorn
from contextlib import asynccontextmanager
from src.database import engine
from src import models

from src.get_users import router as login_router
from src.auth import router as registration_router
from src.logout import router as logout_router
#from src.wallet import router as wallet_router

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(login_router)
app.include_router(registration_router)
app.include_router(logout_router)
#app.include_router(wallet_router)
     
@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown")
    
if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    except asyncio.exceptions.CancelledError:
        print("Server shutdown due to CancelledError")