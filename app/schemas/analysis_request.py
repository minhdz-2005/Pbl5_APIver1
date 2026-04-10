from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from enum import Enum

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    CRAWLING = "CRAWLING"
    ANALYZING_AI = "ANALYZING_AI"
    GENERATING_IMAGES = "GENERATING_IMAGES"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AnalysisRequestBase(BaseModel):
    project_id: str
    category_name: str
    target_style_id: Optional[str] = None
    selected_trend_image_ids: List[str] = []

class AnalysisRequestCreate(AnalysisRequestBase):
    pass

class AnalysisRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    selected_trend_image_ids: Optional[List[str]] = None
    # Thường dùng để cập nhật updated_at tự động khi đổi trạng thái

class AnalysisRequestRead(AnalysisRequestBase):
    id: str = Field(..., alias="_id")
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )