import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from fastapi import Depends, Form, Query
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    
    username: Annotated[str, MinLen(4), MaxLen(40)]
    email: Annotated[EmailStr, MinLen(5), MaxLen(40)]
    password: Annotated[str, Form()]
    
class UserLogin(BaseModel):
    email: str
    password: str
        
        
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class changepassword(BaseModel):
    email:str
    old_password:str
    new_password:str


class TokenCreate(BaseModel):
    user_id:str
    access_token:str
    refresh_token:str
    status:bool
    created_date:datetime.datetime