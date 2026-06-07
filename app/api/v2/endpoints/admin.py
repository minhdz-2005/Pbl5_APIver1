from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# Cộng thêm credit cho user bằng id (Dùng cho Admin)
@router.patch("/users/topup/{user_id}")
async def topup_user_credit(
    user_id: str,
    amount: int,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cộng thêm credit cho user bằng id (Dùng cho Admin)
    """
    repo = UserRepository(db)
    updated_user = await repo.topup_credit(user_id, amount)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return { 
        "success": True,
        "newBalance": updated_user["available_credits"]
    }
