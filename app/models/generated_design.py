from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class GeneratedDesignModel(BaseModel):
    request_id: str  # Liên kết với bảng Analysis_Request
    design_image_url: str
    user_rating: Optional[int] = Field(None, ge=1, le=5) # Đánh giá từ 1-5 sao
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True