from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.core.database import get_database
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription_plan import SubscriptionPlanRead
from app.repositories.transaction_repository import TransactionRepository


router = APIRouter()

@router.get("/plans", response_model=List[SubscriptionPlanRead])
async def get_billing_plans(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Lấy danh sách các gói dịch vụ để hiển thị lên bảng giá (Pricing Table).
    Dữ liệu đã bao gồm is_popular và danh sách features.
    """
    repo = SubscriptionRepository(db)
    return await repo.get_all()

@router.get("/history", response_model=List[dict])
async def get_billing_history(
    user_id: str, # Sau này sẽ lấy từ Token
    limit: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy lịch sử giao dịch credit của người dùng.
    Bao gồm cả nạp tiền (TOP_UP) và sử dụng (USAGE).
    """
    repo = TransactionRepository(db)
    
    # Lấy dữ liệu từ Repository
    transactions = await repo.get_history_by_user(user_id, limit=limit)
    
    # Mapping lại dữ liệu theo định dạng FE yêu cầu
    history = []
    for tx in transactions:
        history.append({
            "id": tx["_id"],
            "type": tx.get("transaction_type"),
            "amount": tx.get("amount"),
            "related_request_id": tx.get("related_request_id"),
            # FE yêu cầu format "YYYY-MM-DD"
            "date": tx.get("created_at").strftime("%Y-%m-%d") if tx.get("created_at") else None
        })
        
    return history