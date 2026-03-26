from pydantic import BaseModel, Field
from typing import List, Optional

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None # ID của danh mục cha

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None

class CategoryRead(CategoryBase):
    id: str = Field(..., alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True