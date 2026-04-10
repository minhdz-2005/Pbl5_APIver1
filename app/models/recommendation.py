from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class RecommendationModel(BaseModel):
    business_id: str
    trend_id: str
    # Add: Nên nhập thêm, Keep: Duy trì, Remove: Nên loại bỏ/Xả kho
    action: str 
    confidence_score: float = Field(..., ge=0.0, le=1.0) # Độ tin cậy của gợi ý (0.0 - 1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True