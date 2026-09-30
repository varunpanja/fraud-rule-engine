from typing import Dict, Any
from app.rules.base_rule import FraudRule, RuleResult
from app.config import settings


class AmountRule(FraudRule):
    """
    Detects unusually high transaction amounts exceeding configured thresholds.
    """
    def __init__(
        self,
        threshold: float = settings.UNUSUAL_AMOUNT_THRESHOLD,
        score: int = settings.AMOUNT_SCORE
    ):
        self.name = "UNUSUAL_AMOUNT"
        self.description = f"Flags transactions with amount exceeding ₹{threshold:,.2f}."
        self.threshold = float(threshold)
        self.default_score = score

    def evaluate(self, transaction: Any, context: Dict[str, Any]) -> RuleResult:
        amount = float(transaction.amount)
        currency = getattr(transaction, "currency", "INR")

        if amount > self.threshold:
            currency_str = f"{currency} " if currency else "INR "
            reason = (
                f"Unusual amount violation: Transaction amount {currency_str}{amount:,.2f} "
                f"exceeds the configured threshold of {currency_str}{self.threshold:,.2f}."
            )
            return RuleResult(
                rule_name=self.name,
                triggered=True,
                score_contribution=self.default_score,
                reason=reason,
                details={
                    "amount": amount,
                    "threshold": self.threshold,
                    "currency": currency,
                    "excess_amount": amount - self.threshold
                }
            )

        return RuleResult(
            rule_name=self.name,
            triggered=False,
            score_contribution=0,
            reason=f"Amount within normal threshold ({amount:,.2f} <= {self.threshold:,.2f}).",
            details={
                "amount": amount,
                "threshold": self.threshold
            }
        )
