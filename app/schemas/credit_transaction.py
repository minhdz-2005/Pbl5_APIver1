from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    TOP_UP = "TOP_UP"
    USAGE = "USAGE"

class CreditTransactionBase(BaseModel):
    user_id: str
    transaction_type: TransactionType
    amount: int
    related_request_id: Optional[str] = None

class CreditTransactionCreate(CreditTransactionBase):
    pass

class CreditTransactionRead(CreditTransactionBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )