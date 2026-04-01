from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.core.config import settings
from app.core.database import get_database
from app.schemas.token import Token
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    # OAuth2PasswordRequestForm giúp FastAPI tự hiểu format form-data (username, password)
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        # 1. Tìm user theo email hoặc username (case-insensitive search)
        user = await db["users"].find_one({
            "$or": [
                {"email": {"$regex": f"^{form_data.username}$", "$options": "i"}},
                {"username": {"$regex": f"^{form_data.username}$", "$options": "i"}}
            ]
        })
        
        if not user:
            logger.warning(f"Login attempt with non-existent credentials: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email/username or password",
            )
        
        # 2. Kiểm tra password_hash tồn tại
        if "password_hash" not in user:
            logger.error(f"User {user.get('email')} has no password_hash field")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User password not properly configured",
            )
            
        # 3. Kiểm tra mật khẩu (sử dụng field password_hash)
        password_valid = security.verify_password(form_data.password, user["password_hash"])
        if not password_valid:
            logger.warning(f"Login attempt with incorrect password for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email/username or password",
            )

        # 4. Tạo Access Token (sử dụng _id từ MongoDB)
        user_id = str(user["_id"])
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = security.create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )

        # 5. Trả về token và thông tin user (trừ mật khẩu)
        logger.info(f"Successful login for user: {user.get('email')} (username: {user.get('username')})")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": user["email"],
                "id": user_id,
                "username": user["username"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )
        