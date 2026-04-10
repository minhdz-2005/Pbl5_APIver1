from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class CreditTransactionModel(BaseModel):
    user_id: str
    # TOP_UP: + credits, USAGE: - credits
    transaction_type: str 
    amount: int  # Số lượng credit thay đổi (ví dụ: +50 hoặc -1)
    related_request_id: Optional[str] = None # Link tới Request ID hoặc Order ID để đối chiếu
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True