from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.schemas.trend_insight import TrendInsightCreate, TrendInsightRead

router = APIRouter()

# --- 1. TẠO TREND INSIGHT MỚI ---
@router.post("/", response_model=TrendInsightRead, status_code=status.HTTP_201_CREATED)
async def create_trend_insight(
    insight_in: TrendInsightCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lưu một kết quả phân tích xu hướng cụ thể cho một yêu cầu (Analysis Request).
    """
    # Kiểm tra request_id có hợp lệ không
    if not ObjectId.is_valid(insight_in.request_id):
        raise HTTPException(status_code=400, detail="request_id không hợp lệ")

    # Kiểm tra xem Analysis Request có tồn tại không
    request_exists = await db["analysis_requests"].find_one({"_id": ObjectId(insight_in.request_id)})
    if not request_exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy Analysis Request tương ứng")

    # Chuyển đổi dữ liệu để lưu vào MongoDB
    from datetime import datetime, timezone
    insight_dict = insight_in.model_dump()
    insight_dict["created_at"] = datetime.now(timezone.utc)
    
    result = await db["trend_insights"].insert_one(insight_dict)
    
    # Trả về kết quả đã tạo
    insight_dict["_id"] = str(result.inserted_id)
    return insight_dict

# --- 2. LẤY DANH SÁCH INSIGHTS THEO ANALYSIS REQUEST ---
@router.get("/request/{request_id}", response_model=List[TrendInsightRead])
async def list_insights_by_request(
    request_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy tất cả các kết quả chi tiết của một phiên phân tích cụ thể.
    """
    if not ObjectId.is_valid(request_id):
        raise HTTPException(status_code=400, detail="request_id không hợp lệ")
        
    insights = []
    cursor = db["trend_insights"].find({"request_id": request_id})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        insights.append(doc)
        
    return insights

# --- 3. LẤY CHI TIẾT MỘT TREND INSIGHT ---
@router.get("/{insight_id}", response_model=TrendInsightRead)
async def get_insight_detail(
    insight_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xem chi tiết một bản ghi insight cụ thể.
    """
    if not ObjectId.is_valid(insight_id):
        raise HTTPException(status_code=400, detail="ID insight không hợp lệ")
        
    insight = await db["trend_insights"].find_one({"_id": ObjectId(insight_id)})
    if not insight:
        raise HTTPException(status_code=404, detail="Không tìm thấy Trend Insight")
        
    insight["_id"] = str(insight["_id"])
    return insight

# --- 4. XÓA TREND INSIGHT ---
@router.delete("/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trend_insight(
    insight_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xóa bỏ một bản ghi insight.
    """
    if not ObjectId.is_valid(insight_id):
        raise HTTPException(status_code=400, detail="ID insight không hợp lệ")
        
    result = await db["trend_insights"].delete_one({"_id": ObjectId(insight_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Xóa thất bại: Insight không tồn tại")
    return None