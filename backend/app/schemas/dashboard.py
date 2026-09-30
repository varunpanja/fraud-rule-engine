from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_transactions: int
    flagged_transactions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    pending_review_count: int
    reviewed_count: int
    cleared_count: int
