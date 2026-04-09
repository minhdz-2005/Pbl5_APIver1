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