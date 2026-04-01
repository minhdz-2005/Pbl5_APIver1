from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict  # Hoặc một UserSchema cụ thể nếu bạn đã có

class TokenPayload(BaseModel):
    sub: Optional[str] = None