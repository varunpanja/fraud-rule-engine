from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.fraud_flag import FraudFlag
from app.schemas.transaction import TransactionCreate
from app.services.transaction_service import process_transaction


def seed_demo_database(db: Session) -> Dict[str, Any]:
    """
    Seeds comprehensive demo scenarios demonstrating all 3 fraud rules,
    combined high-risk conditions, normal baseline transactions, and review states.
    """
    # Clear existing demo data
    db.query(FraudFlag).delete()
    db.query(Transaction).delete()
    db.commit()

    base_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(hours=2)

    created_txns = []

    # =========================================================================
    # 1. BASELINE NORMAL TRANSACTIONS
    # =========================================================================
    normal_scenarios = [
        ("ACC1001", 2400.0, base_time, 17.3850, 78.4867, "Hyderabad", "PURCHASE"),
        ("ACC1001", 3500.0, base_time + timedelta(minutes=45), 17.4000, 78.4900, "Hyderabad", "TRANSFER"),
        ("ACC1002", 1200.0, base_time + timedelta(minutes=10), 12.9716, 77.5946, "Bengaluru", "PURCHASE"),
        ("ACC1003", 5000.0, base_time + timedelta(minutes=20), 19.0760, 72.8777, "Mumbai", "WITHDRAWAL"),
    ]
    for acc, amt, ts, lat, lon, loc, tx_type in normal_scenarios:
        tx_data = TransactionCreate(
            account_id=acc,
            amount=amt,
            currency="INR",
            timestamp=ts,
            latitude=lat,
            longitude=lon,
            location=loc,
            transaction_type=tx_type
        )
        tx, eval_res, _, _ = process_transaction(db, tx_data)
        created_txns.append(tx)

    # =========================================================================
    # 2. RULE 1: VELOCITY BREACH (6 transactions within 3 minutes)
    # =========================================================================
    vel_time = base_time + timedelta(hours=1)
    for i in range(6):
        tx_data = TransactionCreate(
            account_id="ACC-VELOCITY",
            amount=3000.0 + (i * 200),
            currency="INR",
            timestamp=vel_time + timedelta(seconds=i * 25),
            latitude=17.3850,
            longitude=78.4867,
            location="Hyderabad",
            transaction_type="TRANSFER"
        )
        tx, eval_res, _, _ = process_transaction(db, tx_data)
        created_txns.append(tx)

    # =========================================================================
    # 3. RULE 2: UNUSUAL AMOUNT BREACH (₹250,000 single transfer)
    # =========================================================================
    # Normal baseline first
    tx_data = TransactionCreate(
        account_id="ACC-AMOUNT",
        amount=4500.0,
        currency="INR",
        timestamp=base_time + timedelta(hours=1, minutes=15),
        latitude=19.0760,
        longitude=72.8777,
        location="Mumbai",
        transaction_type="PURCHASE"
    )
    process_transaction(db, tx_data)

    # Huge transaction exceeding ₹100,000 threshold
    tx_data = TransactionCreate(
        account_id="ACC-AMOUNT",
        amount=250000.0,
        currency="INR",
        timestamp=base_time + timedelta(hours=1, minutes=20),
        latitude=19.0760,
        longitude=72.8777,
        location="Mumbai",
        transaction_type="TRANSFER"
    )
    tx, eval_res, _, _ = process_transaction(db, tx_data)
    created_txns.append(tx)

    # =========================================================================
    # 4. RULE 3: IMPOSSIBLE GEOGRAPHICAL LOCATION (Hyderabad -> London in 5 mins)
    # =========================================================================
    geo_time = base_time + timedelta(hours=1, minutes=30)
    # 1st txn in Hyderabad
    tx_data = TransactionCreate(
        account_id="ACC-TRAVEL",
        amount=8500.0,
        currency="INR",
        timestamp=geo_time,
        latitude=17.3850,
        longitude=78.4867,
        location="Hyderabad, India",
        transaction_type="PURCHASE"
    )
    process_transaction(db, tx_data)

    # 2nd txn 5 mins later in London (>7,700 km away = ~92,400 km/h)
    tx_data = TransactionCreate(
        account_id="ACC-TRAVEL",
        amount=12000.0,
        currency="INR",
        timestamp=geo_time + timedelta(minutes=5),
        latitude=51.5074,
        longitude=-0.1278,
        location="London, UK",
        transaction_type="PURCHASE"
    )
    tx, eval_res, _, _ = process_transaction(db, tx_data)
    created_txns.append(tx)

    # =========================================================================
    # 5. MULTI-RULE HIGH-RISK BREACH (Amount + Impossible Geo = Score 70 / HIGH)
    # =========================================================================
    crit_time = base_time + timedelta(hours=1, minutes=45)
    # 1st txn in Tokyo
    tx_data = TransactionCreate(
        account_id="ACC-CRITICAL",
        amount=5000.0,
        currency="INR",
        timestamp=crit_time,
        latitude=35.6762,
        longitude=139.6503,
        location="Tokyo, Japan",
        transaction_type="PURCHASE"
    )
    process_transaction(db, tx_data)

    # 2nd txn 8 mins later in New York for ₹350,000 (Triggers Amount + Geo)
    tx_data = TransactionCreate(
        account_id="ACC-CRITICAL",
        amount=350000.0,
        currency="INR",
        timestamp=crit_time + timedelta(minutes=8),
        latitude=40.7128,
        longitude=-74.0060,
        location="New York, USA",
        transaction_type="TRANSFER"
    )
    tx, eval_res, _, _ = process_transaction(db, tx_data)
    created_txns.append(tx)

    # =========================================================================
    # 6. SET SOME FLAGS TO 'REVIEWED' AND 'CLEARED' FOR WORKFLOW DEMO
    # =========================================================================
    # Find some existing flags to illustrate state changes
    flags = db.query(FraudFlag).all()
    if len(flags) >= 2:
        # Mark 1 as REVIEWED
        flags[0].status = "REVIEWED"
        flags[0].reviewer_notes = "Investigated by Senior Fraud Analyst. Customer confirmed unusual travel."
        flags[0].reviewed_at = datetime.utcnow()

        # Mark 1 as CLEARED
        if len(flags) >= 3:
            flags[1].status = "CLEARED"
            flags[1].reviewer_notes = "False positive. Authorized bulk payroll transfer verified with account manager."
            flags[1].reviewed_at = datetime.utcnow()

        db.commit()

    total_tx = db.query(Transaction).count()
    total_flags = db.query(FraudFlag).count()

    return {
        "message": "Demo data successfully seeded!",
        "total_transactions": total_tx,
        "flagged_transactions": total_flags,
        "scenarios_included": [
            "Baseline normal transactions (ACC1001, ACC1002, ACC1003)",
            "Velocity rule violation (ACC-VELOCITY: 6 transactions in 2 mins)",
            "Unusual amount violation (ACC-AMOUNT: INR 250,000 transfer)",
            "Impossible geographical travel (ACC-TRAVEL: Hyderabad -> London in 5 mins)",
            "High-risk multi-rule violation (ACC-CRITICAL: Tokyo -> NYC in 8 mins + INR 350,000)",
            "Audited workflow examples (1 REVIEWED flag, 1 CLEARED flag)"
        ]
    }
