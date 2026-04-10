from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class StylePresetModel(BaseModel):
    display_name: str  # Tên hiển thị (ví dụ: "Vintage 90s")
    ai_prompt_text: str # Prompt thực tế gửi cho AI
    thumbnail_url: Optional[str] = None # Ảnh đại diện cho phong cách này
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True