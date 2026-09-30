from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.transaction import Transaction
from app.models.fraud_flag import FraudFlag
from app.schemas.transaction import TransactionCreate
from app.engine.fraud_engine import default_engine, EvaluationResult
from app.services.notification_service import notification_service
from app.config import settings


def get_historical_context(db: Session, account_id: str, current_time: datetime, exclude_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Builds historical context for the given account:
    - recent_transactions: All transactions within the velocity time window
    - last_transaction: The single most recent transaction prior to current_time
    """
    window_delta = timedelta(minutes=settings.VELOCITY_WINDOW_MINUTES)
    window_start = current_time - window_delta

    # Query recent transactions in velocity window
    recent_query = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.timestamp >= window_start,
        Transaction.timestamp <= current_time
    )
    if exclude_id:
        recent_query = recent_query.filter(Transaction.id != exclude_id)
    recent_transactions = recent_query.order_by(desc(Transaction.timestamp)).all()

    # Query last transaction strictly before or at current_time
    last_query = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.timestamp <= current_time
    )
    if exclude_id:
        last_query = last_query.filter(Transaction.id != exclude_id)
    last_transaction = last_query.order_by(desc(Transaction.timestamp)).first()

    return {
        "recent_transactions": recent_transactions,
        "last_transaction": last_transaction,
        "window_start": window_start,
        "current_time": current_time
    }


def process_transaction(
    db: Session,
    tx_data: TransactionCreate
) -> Tuple[Transaction, EvaluationResult, bool, str]:
    """
    Ingests a transaction, evaluates fraud rules, persists flags, and dispatches alerts.
    """
    # 1. Create Transaction entity
    transaction = Transaction(
        account_id=tx_data.account_id,
        amount=tx_data.amount,
        currency=tx_data.currency,
        timestamp=tx_data.timestamp,
        latitude=tx_data.latitude,
        longitude=tx_data.longitude,
        location=tx_data.location,
        transaction_type=tx_data.transaction_type,
        created_at=datetime.utcnow()
    )
    db.add(transaction)
    db.flush()  # Flush to generate transaction.id

    # 2. Gather historical context for rule evaluation
    context = get_historical_context(db, tx_data.account_id, tx_data.timestamp, exclude_id=transaction.id)

    # 3. Evaluate rules using core FraudEngine
    eval_result: EvaluationResult = default_engine.evaluate(transaction, context)

    # 4. If flagged by any rule, persist FraudFlag record
    if eval_result.is_flagged:
        triggered_dicts = [r.to_dict() for r in eval_result.triggered_rules]
        fraud_flag = FraudFlag(
            transaction_id=transaction.id,
            risk_score=eval_result.total_score,
            risk_level=eval_result.risk_level,
            status="PENDING",
            created_at=datetime.utcnow()
        )
        fraud_flag.triggered_rules = triggered_dicts
        db.add(fraud_flag)

    # 5. Check for High-Risk notification dispatch
    notification_sent = False
    notification_status = "Not required for non-high risk transaction."
    if eval_result.risk_level == "HIGH":
        notification_sent, notification_status = notification_service.send_high_risk_alert(transaction, eval_result)

    db.commit()
    db.refresh(transaction)

    return transaction, eval_result, notification_sent, notification_status
