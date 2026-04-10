from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class RawTrendDataModel(BaseModel):
    trend_id: Optional[str] = None  # Có thể null nếu dữ liệu mới thu thập chưa được phân loại trend
    source_type: str  # TikTok, Instagram, Shopee, Pinterest...
    content_type: str # Video, Post, Product_Review, Search_Query...
    raw_payload: Dict[str, Any]  # Lưu trữ JSON thô thu thập được
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True