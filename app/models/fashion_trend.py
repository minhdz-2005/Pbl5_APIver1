from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class FashionTrendModel(BaseModel):
    category_id: str  # Liên kết với bảng Categories
    trend_name: str
    color_code: Optional[str] = None # Mã màu HEX (ví dụ: #FF5733)
    material: Optional[str] = None   # Chất liệu (Linen, Silk, Denim...)
    style: Optional[str] = None      # Phong cách (Minimalist, Y2K, Office-core...)
    popularity_score: float = Field(default=0.0, ge=0.0, le=100.0) # Độ hot (0-100)
    season: str                      # Spring/Summer 2026, Fall/Winter...
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True