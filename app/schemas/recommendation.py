from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class ActionEnum(str, Enum):
    ADD = "Add"
    KEEP = "Keep"
    REMOVE = "Remove"

class RecommendationBase(BaseModel):
    business_id: str
    trend_id: str
    action: ActionEnum
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationRead(RecommendationBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )