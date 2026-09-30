from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RuleResult:
    """
    Standardized result returned by every fraud rule evaluation.
    """
    rule_name: str
    triggered: bool
    score_contribution: int
    reason: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "triggered": self.triggered,
            "score_contribution": self.score_contribution if self.triggered else 0,
            "reason": self.reason,
            "details": self.details or {}
        }


class FraudRule(ABC):
    """
    Abstract Base Class for all fraud detection rules.
    Any new rule simply subclasses FraudRule and implements the evaluate() method.
    The core FraudEngine executes registered rules generically without modification.
    """
    name: str = "BaseRule"
    description: str = "Base fraud detection rule interface"
    default_score: int = 0

    @abstractmethod
    def evaluate(self, transaction: Any, context: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the transaction against the rule logic.
        
        :param transaction: The current transaction model/schema object.
        :param context: Dictionary containing historical context, e.g.:
                        - 'recent_transactions': List of past transactions within time window
                        - 'last_transaction': The most recent previous transaction for this account
                        - 'account_history': Additional account metadata or stats
        :return: RuleResult object detailing whether rule triggered and score contribution.
        """
        pass
