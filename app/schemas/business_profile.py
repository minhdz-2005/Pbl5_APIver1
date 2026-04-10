from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class BusinessProfileBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    target_market: str = Field(..., max_length=100)
    business_scale: str = Field(..., max_length=50)
    interest_categories: List[str] = []

class BusinessProfileCreate(BusinessProfileBase):
    user_id: str  # Bắt buộc khi tạo profile lần đầu

class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    target_market: Optional[str] = None
    business_scale: Optional[str] = None
    interest_categories: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class BusinessProfileRead(BusinessProfileBase):
    id: str = Field(..., alias="_id")
    user_id: str
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )