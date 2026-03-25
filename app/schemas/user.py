from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "Admin"
    USER = "User"

# Schema chung (Base)
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.USER

# Schema dùng khi Đăng ký (Cần password)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# Schema dùng khi Trả về (Không có password)
class UserRead(UserBase):
    id: str = Field(..., alias="_id") # MongoDB dùng _id
    created_at: datetime

    class Config:
        # Cho phép Pydantic đọc dữ liệu từ dict hoặc object 
        from_attributes = True
        populate_by_name = True

# Thêm class này vào app/schemas/user.py
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None