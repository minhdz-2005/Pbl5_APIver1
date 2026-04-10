from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class GeneratedDesignBase(BaseModel):
    request_id: str
    design_image_url: str
    user_rating: Optional[int] = Field(None, ge=1, le=5)

class GeneratedDesignCreate(GeneratedDesignBase):
    pass

class GeneratedDesignUpdate(BaseModel):
    user_rating: Optional[int] = Field(None, ge=1, le=5)

class GeneratedDesignRead(GeneratedDesignBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )