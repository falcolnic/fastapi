import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from fastapi import Depends, Form
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class User(BaseModel):
    email: str
    password: str
    provider: Optional[str]
    
class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    
    username: Annotated[str, MinLen(3), MaxLen(40)]
    email: Annotated[EmailStr, MinLen(5), MaxLen(40)]
    password: Optional[str]
    
class UserLogin(BaseModel):
    email: str
    password: str
    otp: str
        
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