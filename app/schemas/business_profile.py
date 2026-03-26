from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class BusinessProfileBase(BaseModel):
    user_id: str
    company_name: str
    target_market: str
    business_scale: str
    interest_categories: List[str]

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    target_market: Optional[str] = None
    business_scale: Optional[str] = None
    interest_categories: Optional[List[str]] = None

class BusinessProfileRead(BusinessProfileBase):
    id: str = Field(..., alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True

class BusinessInterestsUpdate(BaseModel):
    category_ids: List[str]

class BusinessInterestsRead(BaseModel):
    business_id: str
    category_ids: List[str]