from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    # MongoDB dùng _id (ObjectId), khi lưu vào DB Pydantic sẽ map qua dict
    username: str
    email: str
    password_hash: str
    role: str = "User"  # Admin/User
    available_credits: int = 10
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True