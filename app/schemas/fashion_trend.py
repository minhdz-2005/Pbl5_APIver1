from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class FashionTrendBase(BaseModel):
    category_id: str
    trend_name: str = Field(..., min_length=2, max_length=200)
    color_code: Optional[str] = None
    material: Optional[str] = None
    style: Optional[str] = None
    popularity_score: float = Field(0.0, ge=0.0, le=100.0)
    season: str

class FashionTrendCreate(FashionTrendBase):
    pass

class FashionTrendUpdate(BaseModel):
    trend_name: Optional[str] = None
    color_code: Optional[str] = None
    material: Optional[str] = None
    style: Optional[str] = None
    popularity_score: Optional[float] = None
    season: Optional[str] = None

class FashionTrendRead(FashionTrendBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )