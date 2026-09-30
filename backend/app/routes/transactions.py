from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.transaction import Transaction
from app.models.fraud_flag import FraudFlag
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionWithFlagDetail,
    FraudEvaluationSummary,
    RuleEvaluationDetail,
)
from app.services.transaction_service import process_transaction

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest a new transaction and evaluate it against all registered fraud detection rules in real-time.
    If high-risk criteria are met, an AWS SNS alert is automatically broadcasted.
    """
    try:
        transaction, eval_result, notif_sent, notif_status = process_transaction(db, payload)

        eval_summary = FraudEvaluationSummary(
            risk_score=eval_result.total_score,
            risk_level=eval_result.risk_level,
            is_flagged=eval_result.is_flagged,
            triggered_rules=[
                RuleEvaluationDetail(
                    rule_name=r.rule_name,
                    triggered=r.triggered,
                    score_contribution=r.score_contribution,
                    reason=r.reason,
                    details=r.details
                )
                for r in eval_result.triggered_rules
            ],
            all_evaluated_rules=[
                RuleEvaluationDetail(
                    rule_name=r.rule_name,
                    triggered=r.triggered,
                    score_contribution=r.score_contribution if r.triggered else 0,
                    reason=r.reason,
                    details=r.details
                )
                for r in eval_result.all_results
            ],
            notification_sent=notif_sent,
            notification_status=notif_status
        )

        return TransactionResponse(
            id=transaction.id,
            account_id=transaction.account_id,
            amount=transaction.amount,
            currency=transaction.currency,
            timestamp=transaction.timestamp,
            latitude=transaction.latitude,
            longitude=transaction.longitude,
            location=transaction.location,
            transaction_type=transaction.transaction_type,
            created_at=transaction.created_at,
            fraud_evaluation=eval_summary
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process transaction: {str(e)}")


@router.get("", response_model=List[TransactionWithFlagDetail])
def list_transactions(
    account_id: Optional[str] = Query(None, description="Filter transactions by Account ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retrieve all transactions with associated fraud flag metadata.
    """
    query = db.query(Transaction).outerjoin(FraudFlag)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    transactions = query.order_by(desc(Transaction.timestamp)).offset(offset).limit(limit).all()

    result = []
    for tx in transactions:
        flag = tx.fraud_flag
        result.append(
            TransactionWithFlagDetail(
                id=tx.id,
                account_id=tx.account_id,
                amount=tx.amount,
                currency=tx.currency,
                timestamp=tx.timestamp,
                latitude=tx.latitude,
                longitude=tx.longitude,
                location=tx.location,
                transaction_type=tx.transaction_type,
                created_at=tx.created_at,
                flag_id=flag.id if flag else None,
                risk_score=flag.risk_score if flag else 0,
                risk_level=flag.risk_level if flag else "LOW",
                status=flag.status if flag else "NORMAL",
                triggered_rules=flag.triggered_rules if flag else [],
                reviewed_at=flag.reviewed_at if flag else None,
                reviewer_notes=flag.reviewer_notes if flag else None
            )
        )
    return result


@router.get("/{id}", response_model=TransactionWithFlagDetail)
def get_transaction(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve single transaction details by ID.
    """
    tx = db.query(Transaction).filter(Transaction.id == id).first()
    if not tx:
        raise HTTPException(status_code=404, detail=f"Transaction with id {id} not found.")

    flag = tx.fraud_flag
    return TransactionWithFlagDetail(
        id=tx.id,
        account_id=tx.account_id,
        amount=tx.amount,
        currency=tx.currency,
        timestamp=tx.timestamp,
        latitude=tx.latitude,
        longitude=tx.longitude,
        location=tx.location,
        transaction_type=tx.transaction_type,
        created_at=tx.created_at,
        flag_id=flag.id if flag else None,
        risk_score=flag.risk_score if flag else 0,
        risk_level=flag.risk_level if flag else "LOW",
        status=flag.status if flag else "NORMAL",
        triggered_rules=flag.triggered_rules if flag else [],
        reviewed_at=flag.reviewed_at if flag else None,
        reviewer_notes=flag.reviewer_notes if flag else None
    )
