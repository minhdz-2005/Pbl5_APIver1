from typing import List

from pydantic import BaseModel, Field

class BusinessProfileModel(BaseModel):
    user_id: str  # Lưu ID của User sở hữu profile này
    company_name: str
    target_market: str
    business_scale: str
    interest_categories: List[str]

    class Config:
        populate_by_name = True