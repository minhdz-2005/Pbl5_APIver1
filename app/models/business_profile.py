from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

class BusinessProfileModel(BaseModel):
    user_id: str  # ID của User từ bảng users
    company_name: str
    target_market: str  # Ví dụ: Nội địa, Quốc tế, Gen Z...
    business_scale: str  # Ví dụ: Small, Medium, Large
    interest_categories: List[str] = [] # Danh sách các mảng thời trang quan tâm
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True