from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class SubscriptionPlanModel(BaseModel):
    plan_name: str  # Free, Pro, Enterprise
    price_per_month: float
    credits_per_month: int
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True