from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.rules.base_rule import FraudRule, RuleResult
from app.rules.velocity_rule import VelocityRule
from app.rules.amount_rule import AmountRule
from app.rules.geo_rule import GeoLocationRule
from app.config import settings


@dataclass
class EvaluationResult:
    total_score: int
    risk_level: str  # LOW, MEDIUM, HIGH
    is_flagged: bool
    triggered_rules: List[RuleResult] = field(default_factory=list)
    all_results: List[RuleResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_score": self.total_score,
            "risk_level": self.risk_level,
            "is_flagged": self.is_flagged,
            "triggered_rules": [r.to_dict() for r in self.triggered_rules],
            "all_evaluated_rules": [r.to_dict() for r in self.all_results]
        }


class FraudEngine:
    """
    Extensible Fraud Rule Engine.
    
    Adheres strictly to the Open-Closed Principle (OCP):
    - Closed for modification: The engine core does not contain rule-specific if/else branches.
    - Open for extension: New rules subclass FraudRule and are registered via register_rule().
    """

    def __init__(self, rules: Optional[List[FraudRule]] = None):
        self._rules: List[FraudRule] = []
        if rules:
            self.register_rules(rules)

    def register_rule(self, rule: FraudRule) -> None:
        """Register a single fraud detection rule."""
        if not isinstance(rule, FraudRule):
            raise TypeError(f"Rule {rule} must inherit from FraudRule base class.")
        self._rules.append(rule)

    def register_rules(self, rules: List[FraudRule]) -> None:
        """Register multiple fraud detection rules."""
        for rule in rules:
            self.register_rule(rule)

    @property
    def registered_rules(self) -> List[FraudRule]:
        return list(self._rules)

    def evaluate(self, transaction: Any, context: Dict[str, Any]) -> EvaluationResult:
        """
        Generically executes all registered rules on the given transaction.
        """
        all_results: List[RuleResult] = []
        triggered_rules: List[RuleResult] = []
        cumulative_score = 0

        # Dynamically evaluate each registered rule
        for rule in self._rules:
            result: RuleResult = rule.evaluate(transaction, context)
            all_results.append(result)
            if result.triggered:
                triggered_rules.append(result)
                cumulative_score += result.score_contribution

        # Cap score at maximum 100
        total_score = min(max(cumulative_score, 0), 100)

        # Classify risk level
        if total_score >= settings.HIGH_RISK_THRESHOLD:
            risk_level = "HIGH"
        elif total_score >= settings.MEDIUM_RISK_THRESHOLD:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        is_flagged = len(triggered_rules) > 0

        return EvaluationResult(
            total_score=total_score,
            risk_level=risk_level,
            is_flagged=is_flagged,
            triggered_rules=triggered_rules,
            all_results=all_results
        )


def create_default_engine() -> FraudEngine:
    """
    Factory function to initialize a FraudEngine populated with default mandatory rules.
    """
    engine = FraudEngine()
    engine.register_rule(VelocityRule())
    engine.register_rule(AmountRule())
    engine.register_rule(GeoLocationRule())
    return engine


# Default singleton instance
default_engine = create_default_engine()
