from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "Admin"
    USER = "User"

# --- Schema Base ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.USER

# --- Schema Create (Request khi Register) ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# --- Schema Read (Dùng cho API Response) ---
class UserRead(UserBase):
    id: str = Field(..., alias="_id") 
    available_credits: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# --- Schema Update ---
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    available_credits: Optional[int] = Field(None, ge=0)
    
    model_config = ConfigDict(from_attributes=True)