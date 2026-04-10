from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class TrendInsightBase(BaseModel):
    request_id: str
    product_name: str = Field(..., min_length=1)
    source_image_url: Optional[str] = None
    positive_rate: float = Field(0.0, ge=0.0, le=100.0)
    total_reviews: int = Field(0, ge=0)

class TrendInsightCreate(TrendInsightBase):
    pass

class TrendInsightRead(TrendInsightBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )