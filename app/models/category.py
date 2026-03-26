from pydantic import BaseModel, Field
from typing import Optional

class CategoryModel(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

    class Config:
        populate_by_name = True