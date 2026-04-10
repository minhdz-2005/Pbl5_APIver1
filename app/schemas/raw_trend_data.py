from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional
from datetime import datetime

class RawTrendDataBase(BaseModel):
    trend_id: Optional[str] = None
    source_type: str = Field(..., example="TikTok")
    content_type: str = Field(..., example="Video")
    raw_payload: Dict[str, Any]

class RawTrendDataCreate(RawTrendDataBase):
    pass

class RawTrendDataRead(RawTrendDataBase):
    id: str = Field(..., alias="_id")
    collected_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class RawTrendDataUpdate(BaseModel):
    trend_id: Optional[str] = None
    # Thường dữ liệu thô ít khi update payload, chủ yếu update trend_id sau khi xử lý AI