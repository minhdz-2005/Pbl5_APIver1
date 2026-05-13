from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class GeneratedDesignModel(BaseModel):
    request_id: str  # Liên kết với bảng Analysis_Request
    ai_job_id: str
    ai_metadata: dict
    design_image_url: list[str]  # mảng URL ảnh thiết kế được sinh ra từ AI Server
    status: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_rating: Optional[int] = Field(None, ge=1, le=5)  # Đánh giá từ 1-5 sao

    class Config:
        populate_by_name = True