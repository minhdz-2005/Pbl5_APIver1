from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.style_repository import StyleRepository
from app.schemas.style_preset import StylePresetCreate, StylePresetRead, StylePresetUpdate

router = APIRouter()

# --- 1. TẠO PHONG CÁCH MẪU MỚI (Admin dùng) ---
@router.post("/", response_model=StylePresetRead, status_code=status.HTTP_201_CREATED)
async def create_style(
    style_in: StylePresetCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo một phong cách thiết kế mới. 
    Lưu ý: ai_prompt_text nên chứa các từ khóa đặc trưng để AI hiểu style này.
    """
    repo = StyleRepository(db)
    # Bạn có thể thêm logic kiểm tra trùng tên display_name nếu cần
    return await repo.create(style_in)

# --- 2. LẤY DANH SÁCH TẤT CẢ PHONG CÁCH (Cho User chọn trên UI) ---
@router.get("/", response_model=List[StylePresetRead])
async def list_styles(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Lấy toàn bộ danh sách các style presets hiện có, sắp xếp theo tên.
    """
    repo = StyleRepository(db)
    return await repo.get_all()

# --- 3. LẤY CHI TIẾT MỘT PHONG CÁCH ---
@router.get("/{style_id}", response_model=StylePresetRead)
async def get_style(style_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Lấy thông tin chi tiết một style cụ thể.
    """
    repo = StyleRepository(db)
    style = await repo.get_by_id(style_id)
    if not style:
        raise HTTPException(status_code=404, detail="Không tìm thấy phong cách thiết kế này")
    return style

# --- 4. CẬP NHẬT PHONG CÁCH ---
@router.patch("/{style_id}", response_model=StylePresetRead)
async def update_style(
    style_id: str, 
    style_in: StylePresetUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cập nhật tên hiển thị, prompt AI hoặc ảnh thumbnail của style.
    """
    repo = StyleRepository(db)
    updated_style = await repo.update(style_id, style_in)
    
    if not updated_style:
        raise HTTPException(status_code=404, detail="Cập nhật thất bại: Style không tồn tại")
    return updated_style

# --- 5. XÓA PHONG CÁCH ---
@router.delete("/{style_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_style(style_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Xóa một style preset. 
    Lưu ý: Nên cẩn thận nếu style này đang được dùng trong các Analysis Requests cũ.
    """
    if not ObjectId.is_valid(style_id):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")
        
    result = await db["style_presets"].delete_one({"_id": ObjectId(style_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy style để xóa")
    return None