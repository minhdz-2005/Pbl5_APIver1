from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# --- 1. LẤY THÔNG TIN USER HIỆN TẠI (Dùng cho Test - Truyền ID qua query) ---
@router.get("/me", response_model=dict)
async def get_my_info_test(
    user_id: str, # Tạm thời truyền trực tiếp ID để test thay vì dùng Token
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Phiên bản TEST: Lấy thông tin user và business profile mà không cần token.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")
        
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    business_profile = await db["business_profiles"].find_one({"user_id": user_id})

    return {
        "user": {
            "id": str(user["_id"]),
            "username": user.get("username"),
            "email": user.get("email"),
            "company_name": business_profile.get("company_name") if business_profile else None,
            "available_credits": user.get("available_credits", 10),
            "role": user.get("role", "User"),
            "created_at": user.get("created_at")
        }
    }

# --- 2. TẠO USER MỚI ---
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db) #
    
    if await repo.check_email_exists(user_in.email): #
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    
    if await repo.check_username_exists(user_in.username): #
        raise HTTPException(status_code=400, detail="Tên người dùng đã tồn tại")
    
    return await repo.create(user_in) # Trả về UserRead với credits mặc định là 10

# --- 3. LIÊT KÊ TẤT CẢ USER ---
@router.get("/", response_model=List[UserRead])
async def list_users(db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    return await repo.get_all() #

# --- 4. LẤY USER THEO ID ---
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id) #
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user

# --- 5. CẬP NHẬT USER ---
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str, 
    user_in: UserUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db)
    updated_user = await repo.update(user_id, user_in) #
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User không tồn tại hoặc ID sai")
    return updated_user

# --- 6. XÓA USER ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    success = await repo.delete(user_id) #
    
    if not success:
        raise HTTPException(status_code=404, detail="Xóa thất bại: User không tồn tại")
    return None