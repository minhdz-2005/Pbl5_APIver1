from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.credit_transaction import CreditTransactionCreate, CreditTransactionRead

router = APIRouter()

# --- 1. TẠO GIAO DỊCH MỚI (Nạp tiền hoặc Sử dụng) ---
@router.post("/", response_model=CreditTransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    tx_in: CreditTransactionCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo một bản ghi giao dịch và tự động cập nhật số dư (available_credits) của User.
    - TOP_UP: amount nên là số dương.
    - USAGE: amount nên là số âm.
    """
    repo = TransactionRepository(db)
    
    # Kiểm tra user_id có hợp lệ không trước khi thực hiện
    if not ObjectId.is_valid(tx_in.user_id):
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
    
    # Kiểm tra User có tồn tại không
    user = await db["users"].find_one({"_id": ObjectId(tx_in.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng để thực hiện giao dịch")

    # Thực hiện tạo transaction (Repo đã xử lý $inc để cập nhật số dư User)
    try:
        new_tx = await repo.create_transaction(tx_in)
        return new_tx
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thực hiện giao dịch: {str(e)}"
        )

# --- 2. LẤY LỊCH SỬ GIAO DỊCH CỦA MỘT USER ---
@router.get("/user/{user_id}", response_model=List[CreditTransactionRead])
async def get_user_transaction_history(
    user_id: str, 
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy danh sách lịch sử giao dịch của một người dùng cụ thể, sắp xếp mới nhất lên đầu.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
        
    repo = TransactionRepository(db)
    history = await repo.get_history_by_user(user_id, limit)
    return history

# --- 3. LẤY CHI TIẾT MỘT GIAO DỊCH THEO ID ---
@router.get("/{tx_id}", response_model=CreditTransactionRead)
async def get_transaction_detail(
    tx_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xem chi tiết một bản ghi giao dịch để đối soát.
    """
    repo = TransactionRepository(db)
    tx = await repo.get_by_id(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi giao dịch")
    return tx

# Lưu ý quan trọng: 
# Chúng ta KHÔNG tạo các endpoint UPDATE hoặc DELETE cho Credit Transactions 
# để đảm bảo tính minh bạch và khả năng kiểm toán (Audit Trail) của hệ thống tài chính.