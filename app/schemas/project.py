from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass # user_id sẽ được lấy từ token người dùng khi gọi API

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None

class ProjectRead(ProjectBase):
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )