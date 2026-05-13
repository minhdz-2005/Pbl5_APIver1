from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class GeneratedDesignBase(BaseModel):
    request_id: str
    ai_job_id: str
    ai_metadata: dict
    design_image_url: list[str]  # mảng URL ảnh thiết kế được sinh ra từ AI Server
    status: str
    updated_at: datetime
    user_rating: Optional[int] = Field(None, ge=1, le=5)

class GeneratedDesignCreate(GeneratedDesignBase):
    pass

class GeneratedDesignUpdate(BaseModel):
    user_rating: Optional[int] = Field(None, ge=1, le=5)

class GeneratedDesignRead(GeneratedDesignBase):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )