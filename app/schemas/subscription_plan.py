from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class SubscriptionPlanBase(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=50)
    price_per_month: float = Field(..., ge=0)
    credits_per_month: int = Field(..., ge=0)
    description: Optional[str] = None
    # Bổ sung vào Base để Create/Read đều có
    is_popular: bool = False
    features: List[str] = []

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    price_per_month: Optional[float] = None
    credits_per_month: Optional[int] = None
    description: Optional[str] = None
    is_popular: Optional[bool] = None
    features: Optional[List[str]] = None

class SubscriptionPlanRead(SubscriptionPlanBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )