from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.core import security
from app.core.config import settings
from app.core.database import get_database
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
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
                "available_credits": user.get("available_credits", 100),
                "role": user.get("role", "User") # Mặc định là "User" nếu không có trường role nào đó trong DB
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
    
@router.post("/register", response_model=RegisterResponse)
async def register_v2(
    register_data: RegisterRequest, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        # 1. Kiểm tra nếu email đã tồn tại
        existing_user = await db["users"].find_one({"email": register_data.email})
        if existing_user:
            logger.warning(f"Attempt to register with existing email: {register_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # 2. Hash password và tạo user mới
        password_hash = security.get_password_hash(register_data.password)

        # Kiểm tra role hợp lệ (có thể tùy chỉnh theo nhu cầu)
        if register_data.role not in ["User", "Admin"]:
            logger.warning(f"Attempt to register with invalid role: {register_data.role}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role specified",
            )

        new_user = {
            "username": register_data.username,
            "email": register_data.email,
            "password_hash": password_hash,
            "role": register_data.role,
            "available_credits": 100,  # Mặc định khi đăng ký mới
            "created_at": datetime.utcnow()
        }
        result = await db["users"].insert_one(new_user)
        user_id = str(result.inserted_id)

        # 3. Trả về thông tin user đã tạo (có thể tùy chỉnh theo nhu cầu)
        return {
            "id": user_id,
            "email": register_data.email,
            "username": register_data.username,
            "available_credits": 100,
            "role": register_data.role,
            "created_at": datetime.utcnow()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"V2 Registration Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )