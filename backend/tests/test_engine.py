from typing import Dict, Any
from app.rules.base_rule import FraudRule, RuleResult
from app.engine.fraud_engine import FraudEngine, create_default_engine
from app.models.transaction import Transaction
from datetime import datetime


class CustomMockRule(FraudRule):
    """Custom rule demonstrating engine extensibility."""
    def __init__(self, should_trigger: bool, score: int = 25):
        self.name = "CUSTOM_NEW_RULE"
        self.description = "A new dynamic rule added without modifying FraudEngine."
        self.should_trigger = should_trigger
        self.default_score = score

    def evaluate(self, transaction: Any, context: Dict[str, Any]) -> RuleResult:
        if self.should_trigger:
            return RuleResult(
                rule_name=self.name,
                triggered=True,
                score_contribution=self.default_score,
                reason="Custom condition satisfied."
            )
        return RuleResult(
            rule_name=self.name,
            triggered=False,
            score_contribution=0,
            reason="Custom condition not met."
        )


def test_extensible_rule_registration():
    engine = FraudEngine()
    assert len(engine.registered_rules) == 0

    # Register custom rule
    custom_rule = CustomMockRule(should_trigger=True, score=25)
    engine.register_rule(custom_rule)
    assert len(engine.registered_rules) == 1

    tx = Transaction(
        id=1,
        account_id="ACC_EXT",
        amount=100.0,
        currency="INR",
        timestamp=datetime.utcnow(),
        latitude=0.0,
        longitude=0.0,
        location="Test",
        transaction_type="TRANSFER"
    )

    result = engine.evaluate(tx, {})
    assert result.is_flagged is True
    assert result.total_score == 25
    assert result.risk_level == "LOW"
    assert len(result.triggered_rules) == 1
    assert result.triggered_rules[0].rule_name == "CUSTOM_NEW_RULE"


def test_score_summation_and_capping():
    engine = FraudEngine()
    # Add rules totaling 130 points
    engine.register_rule(CustomMockRule(should_trigger=True, score=50))
    engine.register_rule(CustomMockRule(should_trigger=True, score=50))
    engine.register_rule(CustomMockRule(should_trigger=True, score=30))

    tx = Transaction(
        id=1,
        account_id="ACC_CAP",
        amount=100.0,
        currency="INR",
        timestamp=datetime.utcnow(),
        latitude=0.0,
        longitude=0.0,
        location="Test",
        transaction_type="TRANSFER"
    )

    result = engine.evaluate(tx, {})
    # Should cap at 100
    assert result.total_score == 100
    assert result.risk_level == "HIGH"
    assert result.is_flagged is True


def test_risk_level_thresholds():
    engine = FraudEngine()
    
    # 0 score -> LOW
    engine.register_rule(CustomMockRule(should_trigger=False, score=0))
    tx = Transaction(id=1, account_id="A", amount=1.0, currency="INR", timestamp=datetime.utcnow(), latitude=0.0, longitude=0.0, location="", transaction_type="")
    res_low = engine.evaluate(tx, {})
    assert res_low.risk_level == "LOW"
    assert res_low.is_flagged is False

    # 30 score -> MEDIUM
    engine2 = FraudEngine([CustomMockRule(should_trigger=True, score=30)])
    res_med = engine2.evaluate(tx, {})
    assert res_med.risk_level == "MEDIUM"
    assert res_med.is_flagged is True

    # 70 score -> HIGH
    engine3 = FraudEngine([CustomMockRule(should_trigger=True, score=70)])
    res_high = engine3.evaluate(tx, {})
    assert res_high.risk_level == "HIGH"
    assert res_high.is_flagged is True
