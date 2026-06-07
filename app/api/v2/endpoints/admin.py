from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from datetime import datetime

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

@router.get("/credit-logs")
async def get_credit_logs(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Lấy thống kê lịch sử giao dịch theo form:
    {
        logs: {
            id: string;
            transactionId: string;
            userId: string;
            userEmail: string;
            type: "TOP_UP" | "USAGE";
            amount: number;
            status: "Success" | "Failed" | "Pending";
            timestamp: string;
        }[];
        total: number;
        totalCreditsIssued: number;
        totalCreditsUsedToday: number;
        }

    """
    repoTransaction = TransactionRepository(db)
    transaction_history = await repoTransaction.get_all_transactions()

    logs = []
    total_credits_issued = 0
    total_credits_used_today = 0
    today = datetime.utcnow().date()

    for tx in transaction_history:
        tx_id = str(tx.get("_id"))
        user_id = tx.get("user_id")
        user_email = None
        notes = []

        # Fetch user email if possible
        if user_id:
            try:
                if ObjectId.is_valid(user_id):
                    user = await db["users"].find_one({"_id": ObjectId(user_id)}, {"email": 1})
                    if user:
                        user_email = user.get("email")
                    else:
                        notes.append("User not found")
                else:
                    notes.append("Invalid user_id")
            except Exception:
                notes.append("Error fetching user")
        else:
            notes.append("Missing user_id")

        # Check related request existence if provided
        related_request_id = tx.get("related_request_id")
        if related_request_id:
            if not ObjectId.is_valid(related_request_id):
                notes.append("Invalid related_request_id")
            else:
                req = await db["analysis_requests"].find_one({"_id": ObjectId(related_request_id)}, {"_id": 1})
                if not req:
                    notes.append("Related request not found")

        # Transaction status: not stored in CreditTransactionModel => mark unknown
        status_val = tx.get("status", "Unknown")

        # Normalize timestamp
        created_at = tx.get("created_at")
        ts_str = None
        created_dt = None
        try:
            if isinstance(created_at, str):
                ts_str = created_at
            elif isinstance(created_at, datetime):
                created_dt = created_at
                ts_str = created_at.isoformat()
            else:
                ts_str = str(created_at)
        except Exception:
            ts_str = None

        # Totals
        t_type = tx.get("transaction_type")
        amount = tx.get("amount", 0) or 0
        if t_type == "TOP_UP":
            try:
                total_credits_issued += int(amount)
            except Exception:
                pass
        if t_type == "USAGE":
            try:
                if created_dt and created_dt.date() == today:
                    total_credits_used_today += abs(int(amount))
            except Exception:
                pass

        log_item = {
            "id": tx_id,
            "transactionId": tx_id,
            "userId": user_id,
            "userEmail": user_email,
            "type": t_type,
            "amount": amount,
            "status": status_val,
            "timestamp": ts_str,
        }
        if notes:
            log_item["note"] = "; ".join(notes)

        logs.append(log_item)

    return {
        "logs": logs,
        "total": len(logs),
        "totalCreditsIssued": total_credits_issued,
        "totalCreditsUsedToday": total_credits_used_today
    }