from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field

class SubscriptionPlanModel(BaseModel):
    plan_name: str
    price_per_month: float
    credits_per_month: int
    description: Optional[str] = None
    # Bổ sung 2 trường mới
    is_popular: bool = False
    features: List[str] = [] 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True