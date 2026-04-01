from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    # MongoDB sử dụng ObjectId, nhưng trong code ta thường dùng str để dễ quản lý
    username: str
    email: str
    password_hash: str
    role: str = "User"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True