from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "Admin"
    USER = "User"
    BUSINESS = "Business" # Thêm role Business dựa trên cấu trúc mới

# --- Schema Base ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.USER

# --- Schema Create ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# --- Schema Read (Dùng cho API Response) ---
class UserRead(UserBase):
    id: str = Field(..., alias="_id") 
    available_credits: int = Field(default=0, ge=0) # Đảm bảo credits không âm
    created_at: datetime

    # Pydantic v2 sử dụng model_config thay cho class Config
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
    
    model_config = ConfigDict(
        from_attributes=True
    )

class UserMeResponse(BaseModel):
    user: UserRead  # Đã bao gồm id, email, role, available_credits
    company_name: Optional[str] = None
    # Nếu bạn muốn trả lại cả token trong response này (dù thường /me không cần)
    # token: Optional[str] = None