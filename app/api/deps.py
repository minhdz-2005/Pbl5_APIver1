from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.schemas.token import TokenPayload
# from app.models.user import User # Import model User của bạn
# from app.db.mongodb import db    # Kết nối MongoDB của bạn

# Định nghĩa đường dẫn để lấy token (khớp với route login bạn vừa viết)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login"
)

async def get_current_user(
    token: str = Depends(reusable_oauth2)
) -> dict: # Hoặc User model
    """
    Dependency dùng để lấy thông tin user hiện tại từ JWT token
    """
    try:
        # 1. Giải mã token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # 2. Tìm user trong Database dựa trên 'sub' (User ID)
    # user = await db["users"].find_one({"_id": token_data.sub})
    
    # Giả lập tìm thấy user
    user = {"id": token_data.sub, "email": "test@example.com", "is_active": True}

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Kiểm tra thêm trạng thái active của user (nếu cần)
    """
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user