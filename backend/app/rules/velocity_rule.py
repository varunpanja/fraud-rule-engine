from typing import Dict, Any
from app.rules.base_rule import FraudRule, RuleResult
from app.config import settings


class VelocityRule(FraudRule):
    """
    Detects excessive transaction frequency for the same account within a short time window.
    Example: More than 5 transactions in 5 minutes by the same account.
    """
    def __init__(
        self,
        window_minutes: int = settings.VELOCITY_WINDOW_MINUTES,
        max_transactions: int = settings.VELOCITY_MAX_TRANSACTIONS,
        score: int = settings.VELOCITY_SCORE
    ):
        self.name = "VELOCITY"
        self.description = f"Flags accounts exceeding {max_transactions} transactions within {window_minutes} minutes."
        self.window_minutes = window_minutes
        self.max_transactions = max_transactions
        self.default_score = score

    def evaluate(self, transaction: Any, context: Dict[str, Any]) -> RuleResult:
        # Retrieve recent transactions for this account from context
        recent_txns = context.get("recent_transactions", [])
        
        # Total transactions including the current one
        count_in_window = len(recent_txns) + 1

        if count_in_window > self.max_transactions:
            reason = (
                f"Velocity violation: Account '{transaction.account_id}' attempted {count_in_window} "
                f"transactions within {self.window_minutes} minutes (Allowed limit: {self.max_transactions})."
            )
            return RuleResult(
                rule_name=self.name,
                triggered=True,
                score_contribution=self.default_score,
                reason=reason,
                details={
                    "window_minutes": self.window_minutes,
                    "max_allowed": self.max_transactions,
                    "transactions_in_window": count_in_window,
                    "account_id": transaction.account_id
                }
            )

        return RuleResult(
            rule_name=self.name,
            triggered=False,
            score_contribution=0,
            reason=f"Transaction velocity normal ({count_in_window}/{self.max_transactions} in {self.window_minutes}m).",
            details={
                "window_minutes": self.window_minutes,
                "max_allowed": self.max_transactions,
                "transactions_in_window": count_in_window
            }
        )
