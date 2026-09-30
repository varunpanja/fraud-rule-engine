from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class FraudFlagUpdate(BaseModel):
    reviewer_notes: Optional[str] = Field(None, description="Reviewer audit note", json_schema_extra={"example": "Verified with account holder via phone."})


class FraudFlagResponse(BaseModel):
    id: int
    transaction_id: int
    risk_score: int
    risk_level: str
    triggered_rules: List[Any]
    status: str
    reviewer_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    # Nested transaction details
    account_id: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    timestamp: Optional[datetime] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    transaction_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
