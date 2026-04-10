from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class BusinessProductModel(BaseModel):
    business_id: str  # ID của Business (thường là User ID)
    category_id: str  # Liên kết với bảng Categories
    product_name: str
    sku: Optional[str] = None # Stock Keeping Unit
    status: str = "Active"    # Active, Out_of_Stock, Discontinued
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True