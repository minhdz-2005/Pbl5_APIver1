from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.core import security
from app.core.config import settings
from app.core.database import get_database
from app.schemas.auth import LoginRequest, LoginResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login_v2(
    login_data: LoginRequest, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        # 1. Tìm user theo email
        user = await db["users"].find_one({"email": login_data.email})
        
        if not user or not security.verify_password(login_data.password, user.get("password_hash", "")):
            logger.warning(f"Failed login attempt for email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # 2. Lấy thông tin Business Profile để có company_name
        # Trong MongoDB, chúng ta dùng user_id (string hoặc ObjectId) để liên kết
        business_profile = await db["business_profiles"].find_one({"user_id": str(user["_id"])})
        
        # 3. Tạo Access Token
        user_id = str(user["_id"])
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = security.create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )

        # 4. Trả về format Response v2
        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": user["email"],
                "company_name": business_profile.get("company_name") if business_profile else None,
                "available_credits": user.get("available_credits", 0),
                "role": user.get("role", "user")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"V2 Login Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )