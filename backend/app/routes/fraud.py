from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.fraud_flag import FraudFlag
from app.models.transaction import Transaction
from app.schemas.fraud_flag import FraudFlagResponse, FraudFlagUpdate

router = APIRouter(prefix="/api/fraud", tags=["Fraud Review Console"])


def map_flag_to_response(flag: FraudFlag) -> FraudFlagResponse:
    tx = flag.transaction
    return FraudFlagResponse(
        id=flag.id,
        transaction_id=flag.transaction_id,
        risk_score=flag.risk_score,
        risk_level=flag.risk_level,
        triggered_rules=flag.triggered_rules,
        status=flag.status,
        reviewer_notes=flag.reviewer_notes,
        created_at=flag.created_at,
        reviewed_at=flag.reviewed_at,
        account_id=tx.account_id if tx else None,
        amount=tx.amount if tx else None,
        currency=tx.currency if tx else None,
        timestamp=tx.timestamp if tx else None,
        location=tx.location if tx else None,
        latitude=tx.latitude if tx else None,
        longitude=tx.longitude if tx else None,
        transaction_type=tx.transaction_type if tx else None
    )


@router.get("/flags", response_model=List[FraudFlagResponse])
def list_fraud_flags(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, REVIEWED, CLEARED)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH)"),
    account_id: Optional[str] = Query(None, description="Filter by Account ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all flagged transactions requiring review with optional filters.
    """
    query = db.query(FraudFlag).join(Transaction)

    if status_filter:
        query = query.filter(FraudFlag.status == status_filter.upper())
    if risk_level:
        query = query.filter(FraudFlag.risk_level == risk_level.upper())
    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    flags = query.order_by(desc(FraudFlag.created_at)).offset(offset).limit(limit).all()
    return [map_flag_to_response(f) for f in flags]


@router.get("/flags/{id}", response_model=FraudFlagResponse)
def get_fraud_flag(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve single fraud flag details.
    """
    flag = db.query(FraudFlag).filter(FraudFlag.id == id).first()
    if not flag:
        raise HTTPException(status_code=404, detail=f"Fraud flag with id {id} not found.")
    return map_flag_to_response(flag)


@router.put("/flags/{id}/review", response_model=FraudFlagResponse)
def mark_flag_reviewed(
    id: int,
    payload: Optional[FraudFlagUpdate] = None,
    db: Session = Depends(get_db)
):
    """
    Mark a flagged transaction as REVIEWED (Confirmed Suspicious / Investigated).
    """
    flag = db.query(FraudFlag).filter(FraudFlag.id == id).first()
    if not flag:
        raise HTTPException(status_code=404, detail=f"Fraud flag with id {id} not found.")

    flag.status = "REVIEWED"
    flag.reviewed_at = datetime.utcnow()
    if payload and payload.reviewer_notes:
        flag.reviewer_notes = payload.reviewer_notes

    db.commit()
    db.refresh(flag)
    return map_flag_to_response(flag)


@router.put("/flags/{id}/clear", response_model=FraudFlagResponse)
def mark_flag_cleared(
    id: int,
    payload: Optional[FraudFlagUpdate] = None,
    db: Session = Depends(get_db)
):
    """
    Mark a flagged transaction as CLEARED (False Positive / Legitimate).
    """
    flag = db.query(FraudFlag).filter(FraudFlag.id == id).first()
    if not flag:
        raise HTTPException(status_code=404, detail=f"Fraud flag with id {id} not found.")

    flag.status = "CLEARED"
    flag.reviewed_at = datetime.utcnow()
    if payload and payload.reviewer_notes:
        flag.reviewer_notes = payload.reviewer_notes

    db.commit()
    db.refresh(flag)
    return map_flag_to_response(flag)
