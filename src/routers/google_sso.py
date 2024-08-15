from fastapi_sso.sso.google import GoogleSSO
from fastapi import Depends, APIRouter, HTTPException, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.utils import create_access_token, authenticate_user
from src.database import get_db
from src import db_crud
from starlette.requests import Request
import src.schemas as schemas
from random import choice
import string

import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
HOST = os.getenv("HOST")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

google_sso = GoogleSSO(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    f"{HOST}/v1/google/callback"
)

router = APIRouter(prefix="/v1/google")

@router.get("/login", tags=['Google SSO'])
async def google_login():
    with google_sso:
        return await google_sso.get_login_redirect(params={
            "prompt": "consent",
            "access_type": "offline"
            })
        
        
@router.get("/callback", tags=['Google SSO'])
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Process login response from Google and return user info"""

    try:
        with google_sso:
            user = await google_sso.verify_and_process(request)
        user_stored = db_crud.get_user(db, user.email, provider=user.provider)
        if not user_stored:
            # Generate a random password (Fix in future)
            random_password = ''.join(choice(string.ascii_letters + string.digits) for _ in range(12))
            user_to_add = schemas.UserCreate(
                username=user.email,
                fullname=user.display_name,
                email=user.email,
                password=None  # Add the random password here
            )
            user_stored = db_crud.add_user(user_to_add, db, provider="google")  # Corrected order of arguments
        access_token = create_access_token(username=user_stored.username, provider=user.provider)
        response = RedirectResponse(url="/v1/login", status_code=status.HTTP_302_FOUND)
        
        return response
    except db_crud.DuplicateError as e:
        raise HTTPException(status_code=403, detail=f"{e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")