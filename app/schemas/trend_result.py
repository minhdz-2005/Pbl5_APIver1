from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from typing import List, Dict, Any, Optional

class ScoringSignals(BaseModel):
    # Sử dụng Dict vì AI Server có thể trả về các thuộc tính động
    additional_signals: Dict[str, Any] = Field(default={}, alias="additionalProp1")

    model_config = ConfigDict(populate_by_name=True)

class TrendResultBase(BaseModel):
    product_name: str
    source_image_url: HttpUrl
    positive_rate: float = Field(ge=0, le=1)
    trend_score: float
    confidence: float = Field(ge=0, le=1)
    total_reviews: int
    style_keywords: List[str]
    scoring_signals: Optional[Dict[str, Any]] = None

class TrendResultCreate(TrendResultBase):
    analysis_request_id: str

class TrendResultUpdate(BaseModel):
    trend_score: Optional[float] = None
    confidence: Optional[float] = None
    style_keywords: Optional[List[str]] = None

class TrendResultRead(TrendResultBase):
    id: str = Field(..., alias="_id")
    analysis_request_id: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )