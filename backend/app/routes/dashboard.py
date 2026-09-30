from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import Transaction
from app.models.fraud_flag import FraudFlag
from app.schemas.dashboard import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated KPIs for the reviewer console dashboard.
    """
    total_tx = db.query(Transaction).count()
    total_flags = db.query(FraudFlag).count()
    high_risk = db.query(FraudFlag).filter(FraudFlag.risk_level == "HIGH").count()
    medium_risk = db.query(FraudFlag).filter(FraudFlag.risk_level == "MEDIUM").count()
    low_risk = db.query(FraudFlag).filter(FraudFlag.risk_level == "LOW").count()
    pending = db.query(FraudFlag).filter(FraudFlag.status == "PENDING").count()
    reviewed = db.query(FraudFlag).filter(FraudFlag.status == "REVIEWED").count()
    cleared = db.query(FraudFlag).filter(FraudFlag.status == "CLEARED").count()

    return DashboardStatsResponse(
        total_transactions=total_tx,
        flagged_transactions=total_flags,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        pending_review_count=pending,
        reviewed_count=reviewed,
        cleared_count=cleared
    )
