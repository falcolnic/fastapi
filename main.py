import asyncio
from fastapi import Depends, FastAPI, Request,HTTPException
from pathlib import Path
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.database import engine
from src import models
from importlib.metadata import version
from sqlalchemy.orm import Session
from src.database import get_db
from src import db_crud

from src.routers.google_sso import router as google_sso_router
from src.auth import router as registration_router
from src.user_management import router as user_management_router
#from src.wallet import router as wallet_router

import os
from dotenv import load_dotenv
load_dotenv()
parent_directory = Path(__file__).parent
templates_path = parent_directory / "templates"
templates = Jinja2Templates(directory=templates_path)

app = FastAPI(title='Authorization')

models.Base.metadata.create_all(bind=engine)

app.include_router(registration_router)
app.include_router(user_management_router)
app.include_router(google_sso_router)
#app.include_router(wallet_router)



@app.get("/", response_class=HTMLResponse, summary="Home page")
def home_page(request: Request, db: Session = Depends(get_db)):
    versions = {
        "fastapi_version": version('fastapi'),
        "fastapi_sso_version": version('fastapi_sso')
    }
    response = templates.TemplateResponse("index.html", {"request": request, "versions": versions})
    return response

@app.get("/privacy_policy", response_class=HTMLResponse, summary="Privacy Policy")
def privacy_policy(request: Request):
    try:
        response = templates.TemplateResponse(
            "privacy_policy.html",
            {
                "request": request,
                "host": os.getenv('HOST'),
                "contact_email": os.getenv('CONTACT_EMAIL')
            }
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


     
@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown")

if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    except asyncio.exceptions.CancelledError:
        print("Server shutdown due to CancelledError")