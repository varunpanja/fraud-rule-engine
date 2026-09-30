from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import Transaction
from app.models.fraud_flag import FraudFlag
from app.services.seed_service import seed_demo_database

router = APIRouter(prefix="/api/demo", tags=["Demo Utilities"])


@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    """
    Seeds demo transactions showcasing all 3 fraud rules, high-risk combinations,
    baseline normal transactions, and review workflow states.
    """
    result = seed_demo_database(db)
    return result


@router.post("/reset")
def reset_data(db: Session = Depends(get_db)):
    """
    Clears all transactions and fraud flags for a clean demo slate.
    """
    db.query(FraudFlag).delete()
    db.query(Transaction).delete()
    db.commit()
    return {"message": "All transactions and fraud flags have been reset."}
