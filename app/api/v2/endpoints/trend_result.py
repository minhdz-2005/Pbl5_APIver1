from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.core.database import get_database # Giả định path của bạn
from app.schemas.trend_result import TrendResultRead, TrendResultUpdate
from app.repositories.trend_repository import TrendRepository
from pydantic import BaseModel

# Test upload service
class UploadTestIn(BaseModel):
    image_url: str
    generated_design_id: str | None = None

from app.services.uploadImgtoCloudinary import upload_image_to_cloudinary

router = APIRouter(prefix="/trend-results", tags=["Trend Results"])

@router.get("/request/{request_id}", response_model=List[TrendResultRead])
async def get_trends_by_analysis(request_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Lấy danh sách tất cả xu hướng của một yêu cầu phân tích."""
    repo = TrendRepository(db)
    results = await repo.get_by_request_id(request_id)
    return results

@router.get("/{trend_id}", response_model=TrendResultRead)
async def get_trend_detail(trend_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Lấy chi tiết một kết quả xu hướng cụ thể."""
    repo = TrendRepository(db)
    trend = await repo.get_one(trend_id)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend result không tồn tại")
    return trend

@router.patch("/{trend_id}", response_model=bool)
async def update_trend(trend_id: str, data_in: TrendResultUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Cập nhật thông số xu hướng (ví dụ: điều chỉnh điểm số thủ công)."""
    repo = TrendRepository(db)
    updated = await repo.update(trend_id, data_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Cập nhật thất bại hoặc không tìm thấy ID")
    return True

@router.delete("/{trend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trend(trend_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Xóa một kết quả xu hướng."""
    repo = TrendRepository(db)
    deleted = await repo.delete(trend_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy ID để xóa")
    return None


@router.post("/test-upload", response_model=dict)
async def test_upload_endpoint(payload: UploadTestIn):
    """Endpoint tạm để test upload ảnh lên Cloudinary.

    Gọi `upload_image_to_cloudinary` và trả về kết quả thô để debug.
    """
    gen_id = payload.generated_design_id or "test"
    result = await upload_image_to_cloudinary(payload.image_url, gen_id)
    return result


@router.get("/debug/cloudinary-config", response_model=dict)
async def debug_cloudinary_config():
    """Return masked Cloudinary configuration presence for debugging (no secrets returned)."""
    from app.core.config import settings

    def mask(s: str | None) -> str | None:
        if not s:
            return None
        if len(s) <= 8:
            return s[:2] + "..."
        return s[:4] + "..." + s[-4:]

    return {
        "has_cloudinary_url": bool(settings.CLOUDINARY_URL),
        "cloudinary_url_masked": mask(settings.CLOUDINARY_URL),
        "has_api_key": bool(settings.CLOUDINARY_API_KEY),
        "cloudinary_api_key_masked": mask(settings.CLOUDINARY_API_KEY),
        "has_cloud_name": bool(settings.CLOUDINARY_CLOUD_NAME),
        "cloudinary_cloud_name_masked": mask(settings.CLOUDINARY_CLOUD_NAME),
    }