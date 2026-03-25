from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead
from typing import List
from app.schemas.user import UserUpdate

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db)
    # Kiểm tra email tồn tại (bạn có thể viết thêm hàm check_email trong repo)
    new_user = await repo.create(user_in)
    return new_user

@router.get("/", response_model=List[UserRead])
async def list_users(db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    return await repo.get_all()

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str, 
    user_in: UserUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db)
    updated_user = await repo.update(user_id, user_in)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found hoặc ID không hợp lệ")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db)
    success = await repo.delete(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy User để xóa hoặc ID không hợp lệ"
        )
    
    # Với status_code 204, FastAPI sẽ tự động trả về body trống
    return None