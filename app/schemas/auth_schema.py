
from pydantic import BaseModel, EmailStr
from typing import Optional




class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str



class LoginRequest(BaseModel):
    email: EmailStr
    password: str




class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"




class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr




class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
