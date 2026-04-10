from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.design_repository import DesignRepository
from app.schemas.generated_design import (
    GeneratedDesignCreate, 
    GeneratedDesignRead, 
    GeneratedDesignUpdate
)

router = APIRouter()

# --- 1. LƯU MẪU THIẾT KẾ MỚI (Thường gọi từ AI Worker) ---
@router.post("/", response_model=GeneratedDesignRead, status_code=status.HTTP_201_CREATED)
async def create_design(
    design_in: GeneratedDesignCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lưu trữ thông tin ảnh thiết kế sau khi AI hoàn tất việc tạo ảnh.
    """
    if not ObjectId.is_valid(design_in.request_id):
        raise HTTPException(status_code=400, detail="request_id không hợp lệ")
    
    repo = DesignRepository(db)
    return await repo.create(design_in)

# --- 2. LẤY TẤT CẢ THIẾT KẾ CỦA MỘT PHIÊN PHÂN TÍCH ---
@router.get("/request/{request_id}", response_model=List[GeneratedDesignRead])
async def list_designs_by_request(
    request_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy danh sách các ảnh thiết kế được tạo ra từ một Analysis Request cụ thể.
    """
    repo = DesignRepository(db)
    return await repo.get_by_request(request_id)

# --- 3. LẤY CHI TIẾT MỘT THIẾT KẾ ---
@router.get("/{design_id}", response_model=GeneratedDesignRead)
async def get_design(
    design_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xem thông tin chi tiết của một bản ghi thiết kế.
    """
    repo = DesignRepository(db)
    design = await repo.get_by_id(design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu thiết kế")
    return design

# --- 4. CẬP NHẬT ĐÁNH GIÁ (USER RATING) ---
@router.patch("/{design_id}/rate", response_model=GeneratedDesignRead)
async def rate_design(
    design_id: str, 
    update_in: GeneratedDesignUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cho phép người dùng đánh giá (1-5 sao) mẫu thiết kế này.
    """
    if update_in.user_rating is None:
        raise HTTPException(status_code=400, detail="Cần cung cấp giá trị user_rating")
        
    repo = DesignRepository(db)
    updated_design = await repo.update_rating(design_id, update_in.user_rating)
    
    if not updated_design:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết kế để đánh giá")
    return updated_design

# --- 5. XÓA MẪU THIẾT KẾ ---
@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_design(
    design_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xóa một bản ghi thiết kế khỏi hệ thống.
    """
    if not ObjectId.is_valid(design_id):
        raise HTTPException(status_code=400, detail="ID thiết kế không hợp lệ")
        
    result = await db["generated_designs"].delete_one({"_id": ObjectId(design_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Thiết kế không tồn tại")
    return None