from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database

# Định nghĩa đường dẫn lấy token (dùng cho Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v2/auth/login")

# Cấu hình context để băm mật khẩu bằng thuật toán bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Tạo JWT Access Token
    :param subject: Thông tin định danh user (thường là User ID hoặc Email)
    :param expires_delta: Thời gian hết hạn tùy chỉnh
    :return: Chuỗi mã hóa JWT
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Payload chứa thông tin token
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Mã hóa với Secret Key và Algorithm từ config
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu người dùng nhập vào có khớp với mã băm trong DB không
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Băm mật khẩu trước khi lưu vào Database
    """
    return pwd_context.hash(password)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Giải mã Token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # 2. Truy vấn Database lấy thông tin User mới nhất
    # Lưu ý: Import ObjectId nếu bạn lưu user_id dưới dạng ObjectId trong MongoDB
    from bson import ObjectId
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    
    if user is None:
        raise credentials_exception
        
    return user