from datetime import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    company_name: Optional[str] = None
    available_credits: int
    role: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str

class RegisterResponse(BaseModel):
    id: str
    email: str
    username: str
    role: str
    available_credits: int
    created_at: datetime

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ChangePasswordResponse(BaseModel):
    detail: str