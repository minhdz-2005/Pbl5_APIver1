from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

class AnalysisRequestModel(BaseModel):
    project_id: str
    category_name: str
    target_style_id: Optional[str] = None
    selected_trend_image_ids: List[str] = [] # Danh sách ID các ảnh trend tham chiếu
    status: str = "PENDING" 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True