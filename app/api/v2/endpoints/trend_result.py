from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.core.database import get_database # Giả định path của bạn
from app.schemas.trend_result import TrendResultRead, TrendResultUpdate
from app.repositories.trend_repository import TrendRepository

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