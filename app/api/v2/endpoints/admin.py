from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.design_repository import DesignRepository
from app.repositories.transaction_repository import TransactionRepository
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

@router.get("/stats")
async def get_system_stats(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Lấy thống kê hệ thống: tổng số user, tổng người dùng tăng trưởng theo tháng, số sub plan đã bán, tỉ lệ gen ảnh thành công, số tiếng trình gen ảnh đang chạy
    {
    totalUsers: number;
    userGrowth: {
        datetime: Date; tháng/năm
        total: Number;
    totalCreditsSold: Number
    successRate: number;
    activeGenerations: number;
    }

    """
    repoUser = UserRepository(db)
    repoTransaction = TransactionRepository(db)
    repoGen = DesignRepository(db)

    total_users = await repoUser.count_users()

    user_growth = await repoUser.get_user_growth_by_month()
    total_credits_sold = await repoTransaction.get_total_credits_sold()
    success_rate = await repoGen.get_success_rate()
    active_generations = await repoGen.count_active_generations()

    return {
        "total_users": total_users,
        "userGrowth": user_growth,
        "totalCreditsSold": total_credits_sold,
        "successRate": success_rate,
        "activeGenerations": active_generations
    }