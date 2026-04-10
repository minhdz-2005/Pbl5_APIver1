from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class ProjectModel(BaseModel):
    user_id: str
    project_name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True