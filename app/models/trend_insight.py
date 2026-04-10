from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class TrendInsightModel(BaseModel):
    request_id: str  # Liên kết với bảng Analysis_Request
    product_name: str
    source_image_url: Optional[str] = None
    positive_rate: float = Field(default=0.0, ge=0.0, le=100.0) # Tỷ lệ % tích cực
    total_reviews: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True