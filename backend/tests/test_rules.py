from datetime import datetime, timedelta
from app.rules.velocity_rule import VelocityRule
from app.rules.amount_rule import AmountRule
from app.rules.geo_rule import GeoLocationRule, haversine_distance_km
from app.models.transaction import Transaction


def test_velocity_rule_triggers_on_excess():
    rule = VelocityRule(window_minutes=5, max_transactions=5, score=30)
    current_time = datetime(2026, 9, 30, 10, 30, 0)
    
    # 5 prior transactions + 1 current = 6 in window (exceeds max_transactions of 5)
    recent_txns = [
        Transaction(
            id=i,
            account_id="ACC100",
            amount=1000.0,
            currency="INR",
            timestamp=current_time - timedelta(minutes=i),
            latitude=17.385,
            longitude=78.486,
            location="Hyderabad",
            transaction_type="TRANSFER"
        )
        for i in range(1, 6)
    ]
    
    current_tx = Transaction(
        id=6,
        account_id="ACC100",
        amount=1000.0,
        currency="INR",
        timestamp=current_time,
        latitude=17.385,
        longitude=78.486,
        location="Hyderabad",
        transaction_type="TRANSFER"
    )
    
    context = {"recent_transactions": recent_txns}
    result = rule.evaluate(current_tx, context)
    
    assert result.triggered is True
    assert result.score_contribution == 30
    assert result.rule_name == "VELOCITY"
    assert "Velocity violation" in result.reason


def test_velocity_rule_passes_within_limit():
    rule = VelocityRule(window_minutes=5, max_transactions=5, score=30)
    current_time = datetime(2026, 9, 30, 10, 30, 0)
    
    # Only 2 prior transactions
    recent_txns = [
        Transaction(
            id=1,
            account_id="ACC100",
            amount=1000.0,
            currency="INR",
            timestamp=current_time - timedelta(minutes=2),
            latitude=17.385,
            longitude=78.486,
            location="Hyderabad",
            transaction_type="TRANSFER"
        )
    ]
    
    current_tx = Transaction(
        id=2,
        account_id="ACC100",
        amount=1000.0,
        currency="INR",
        timestamp=current_time,
        latitude=17.385,
        longitude=78.486,
        location="Hyderabad",
        transaction_type="TRANSFER"
    )
    
    context = {"recent_transactions": recent_txns}
    result = rule.evaluate(current_tx, context)
    
    assert result.triggered is False
    assert result.score_contribution == 0


def test_amount_rule_triggers_on_unusual_amount():
    rule = AmountRule(threshold=100000.0, score=30)
    
    current_tx = Transaction(
        id=1,
        account_id="ACC200",
        amount=250000.0,
        currency="INR",
        timestamp=datetime.utcnow(),
        latitude=17.385,
        longitude=78.486,
        location="Hyderabad",
        transaction_type="TRANSFER"
    )
    
    result = rule.evaluate(current_tx, {})
    assert result.triggered is True
    assert result.score_contribution == 30
    assert result.rule_name == "UNUSUAL_AMOUNT"
    assert "250,000" in result.reason


def test_amount_rule_passes_on_normal_amount():
    rule = AmountRule(threshold=100000.0, score=30)
    
    current_tx = Transaction(
        id=1,
        account_id="ACC200",
        amount=5000.0,
        currency="INR",
        timestamp=datetime.utcnow(),
        latitude=17.385,
        longitude=78.486,
        location="Hyderabad",
        transaction_type="TRANSFER"
    )
    
    result = rule.evaluate(current_tx, {})
    assert result.triggered is False
    assert result.score_contribution == 0


def test_geo_rule_haversine_and_impossible_travel():
    rule = GeoLocationRule(max_speed_kmph=900.0, score=40)
    
    # 10:00 AM in Hyderabad (lat 17.3850, lon 78.4867)
    t1 = datetime(2026, 9, 30, 10, 0, 0)
    prev_tx = Transaction(
        id=1,
        account_id="ACC300",
        amount=500.0,
        currency="INR",
        timestamp=t1,
        latitude=17.3850,
        longitude=78.4867,
        location="Hyderabad",
        transaction_type="PURCHASE"
    )
    
    # 10:05 AM in London (lat 51.5074, lon -0.1278) -> ~7700 km in 5 mins = ~92400 km/h
    t2 = datetime(2026, 9, 30, 10, 5, 0)
    current_tx = Transaction(
        id=2,
        account_id="ACC300",
        amount=1500.0,
        currency="INR",
        timestamp=t2,
        latitude=51.5074,
        longitude=-0.1278,
        location="London",
        transaction_type="PURCHASE"
    )
    
    context = {"last_transaction": prev_tx}
    result = rule.evaluate(current_tx, context)
    
    assert result.triggered is True
    assert result.score_contribution == 40
    assert result.rule_name == "IMPOSSIBLE_LOCATION"
    assert "Impossible travel" in result.reason
    assert result.details["calculated_speed_kmph"] > 900.0


def test_geo_rule_passes_on_realistic_movement():
    rule = GeoLocationRule(max_speed_kmph=900.0, score=40)
    
    # Hyderabad to Bengaluru (~500 km) in 2 hours (~250 km/h flight)
    t1 = datetime(2026, 9, 30, 10, 0, 0)
    prev_tx = Transaction(
        id=1,
        account_id="ACC300",
        amount=500.0,
        currency="INR",
        timestamp=t1,
        latitude=17.3850,
        longitude=78.4867,
        location="Hyderabad",
        transaction_type="PURCHASE"
    )
    
    t2 = datetime(2026, 9, 30, 12, 0, 0)
    current_tx = Transaction(
        id=2,
        account_id="ACC300",
        amount=1500.0,
        currency="INR",
        timestamp=t2,
        latitude=12.9716,
        longitude=77.5946,
        location="Bengaluru",
        transaction_type="PURCHASE"
    )
    
    context = {"last_transaction": prev_tx}
    result = rule.evaluate(current_tx, context)
    
    assert result.triggered is False
    assert result.score_contribution == 0
