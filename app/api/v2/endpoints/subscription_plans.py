from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanRead, SubscriptionPlanUpdate

router = APIRouter()

# --- 1. TẠO GÓI SUBSCRIPTION MỚI (Dành cho Admin/Internal) ---
@router.post("/", response_model=SubscriptionPlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_in: SubscriptionPlanCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo gói mới. Giờ đây bạn có thể truyền thêm:
    - is_popular: true/false
    - features: ["Tính năng 1", "Tính năng 2"]
    """
    repo = SubscriptionRepository(db)
    
    existing_plan = await repo.get_by_name(plan_in.plan_name)
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gói dịch vụ '{plan_in.plan_name}' đã tồn tại"
        )
    
    return await repo.create(plan_in)

# --- 2. LẤY DANH SÁCH TẤT CẢ CÁC GÓI ---
@router.get("/", response_model=List[SubscriptionPlanRead])
async def list_plans(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Lấy danh sách gói. Kết quả trả về sẽ bao gồm đầy đủ features 
    và is_popular để FE hiển thị bảng giá.
    """
    repo = SubscriptionRepository(db)
    # Repo của bạn đã có .sort("price_per_month", 1) là rất tốt cho FE
    return await repo.get_all()

# --- 3. LẤY CHI TIẾT MỘT GÓI THEO ID ---
@router.get("/{plan_id}", response_model=SubscriptionPlanRead)
async def get_plan(plan_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    if not ObjectId.is_valid(plan_id):
        raise HTTPException(status_code=400, detail="ID gói không hợp lệ")

    repo = SubscriptionRepository(db)
    # Nếu bạn đã thêm get_by_id vào Repo thì nên dùng:
    # plan = await repo.get_by_id(plan_id)
    
    # Cách hiện tại (truy vấn trực tiếp) vẫn chạy đúng nhưng chưa đẹp:
    plan = await db["subscription_plans"].find_one({"_id": ObjectId(plan_id)})
    if not plan:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói dịch vụ")
    
    plan["_id"] = str(plan["_id"])
    return plan

# --- 4. CẬP NHẬT GÓI ---
@router.patch("/{plan_id}", response_model=SubscriptionPlanRead)
async def update_plan(
    plan_id: str, 
    plan_in: SubscriptionPlanUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cập nhật thông tin gói, bao gồm cả việc sửa danh sách features hoặc đổi gói popular.
    """
    repo = SubscriptionRepository(db)
    updated_plan = await repo.update(plan_id, plan_in)
    
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cập nhật thất bại: Gói không tồn tại"
        )
    return updated_plan

# --- 5. XÓA GÓI ---
@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(plan_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = SubscriptionRepository(db)
    success = await repo.delete(plan_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy gói để xóa"
        )
    return None