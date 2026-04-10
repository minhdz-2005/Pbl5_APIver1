from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class BusinessProductBase(BaseModel):
    category_id: str
    product_name: str = Field(..., min_length=2, max_length=200)
    sku: Optional[str] = None
    status: str = "Active"

class BusinessProductCreate(BusinessProductBase):
    business_id: str

class BusinessProductUpdate(BaseModel):
    category_id: Optional[str] = None
    product_name: Optional[str] = None
    sku: Optional[str] = None
    status: Optional[str] = None

class BusinessProductRead(BusinessProductBase):
    id: str = Field(..., alias="_id")
    business_id: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )