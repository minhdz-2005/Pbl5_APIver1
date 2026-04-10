from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class StylePresetBase(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=100)
    ai_prompt_text: str = Field(..., min_length=10)
    thumbnail_url: Optional[str] = None

class StylePresetCreate(StylePresetBase):
    pass

class StylePresetUpdate(BaseModel):
    display_name: Optional[str] = None
    ai_prompt_text: Optional[str] = None
    thumbnail_url: Optional[str] = None

class StylePresetRead(StylePresetBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )