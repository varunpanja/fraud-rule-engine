from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    account_id: str = Field(..., description="Unique identifier for the account/user", json_schema_extra={"example": "ACC1001"})
    amount: float = Field(..., gt=0, description="Transaction amount", json_schema_extra={"example": 250000.0})
    currency: str = Field(default="INR", description="Currency code", json_schema_extra={"example": "INR"})
    timestamp: datetime = Field(..., description="ISO 8601 timestamp", json_schema_extra={"example": "2026-09-30T10:30:00"})
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate", json_schema_extra={"example": 17.3850})
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate", json_schema_extra={"example": 78.4867})
    location: str = Field(..., description="Human-readable city/location name", json_schema_extra={"example": "Hyderabad"})
    transaction_type: str = Field(default="TRANSFER", description="Type of transaction (TRANSFER, PURCHASE, WITHDRAWAL)", json_schema_extra={"example": "TRANSFER"})


class RuleEvaluationDetail(BaseModel):
    rule_name: str
    triggered: bool
    score_contribution: int
    reason: str
    details: Optional[dict] = None


class FraudEvaluationSummary(BaseModel):
    risk_score: int
    risk_level: str  # LOW, MEDIUM, HIGH
    is_flagged: bool
    triggered_rules: List[RuleEvaluationDetail]
    all_evaluated_rules: List[RuleEvaluationDetail]
    notification_sent: bool = False
    notification_status: str = "N/A"


class TransactionResponse(BaseModel):
    id: int
    account_id: str
    amount: float
    currency: str
    timestamp: datetime
    latitude: float
    longitude: float
    location: str
    transaction_type: str
    created_at: datetime
    fraud_evaluation: Optional[FraudEvaluationSummary] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionWithFlagDetail(BaseModel):
    id: int
    account_id: str
    amount: float
    currency: str
    timestamp: datetime
    latitude: float
    longitude: float
    location: str
    transaction_type: str
    created_at: datetime
    flag_id: Optional[int] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    triggered_rules: Optional[List[Any]] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
