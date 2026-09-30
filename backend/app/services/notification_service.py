import logging
import json
from typing import Tuple, Any
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service responsible for dispatching alerts when high-risk transactions are detected.
    Supports AWS SNS with automated graceful fallback for local development/offline demos.
    """

    def __init__(self):
        self.aws_region = settings.AWS_REGION
        self.access_key = settings.AWS_ACCESS_KEY_ID
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.topic_arn = settings.AWS_SNS_TOPIC_ARN

    def is_aws_configured(self) -> bool:
        return bool(self.topic_arn and self.access_key and self.secret_key)

    def send_high_risk_alert(self, transaction: Any, eval_result: Any) -> Tuple[bool, str]:
        """
        Sends an alert for a high-risk transaction.
        
        :param transaction: The transaction model or schema instance.
        :param eval_result: EvaluationResult object from FraudEngine.
        :return: Tuple of (success: bool, status_message: str)
        """
        # Format human-readable rule summaries
        triggered_list = []
        for r in getattr(eval_result, "triggered_rules", []):
            rule_name = r.rule_name if hasattr(r, "rule_name") else r.get("rule_name", "UNKNOWN")
            reason = r.reason if hasattr(r, "reason") else r.get("reason", "")
            score = r.score_contribution if hasattr(r, "score_contribution") else r.get("score_contribution", 0)
            triggered_list.append(f"  * [{rule_name} (+{score})]: {reason}")

        rules_text = "\n".join(triggered_list) if triggered_list else "  * No specific rules captured."

        amount_str = f"{getattr(transaction, 'currency', 'INR')} {getattr(transaction, 'amount', 0.0):,.2f}"
        
        subject = f"[HIGH RISK FRAUD ALERT] Transaction #{getattr(transaction, 'id', 'N/A')} - Account {getattr(transaction, 'account_id', 'N/A')}"
        
        message = (
            f"HIGH RISK FRAUD ALERT DETECTED\n"
            f"==================================================\n"
            f"Transaction ID:   {getattr(transaction, 'id', 'N/A')}\n"
            f"Account ID:       {getattr(transaction, 'account_id', 'N/A')}\n"
            f"Amount:           {amount_str}\n"
            f"Location:         {getattr(transaction, 'location', 'N/A')} ({getattr(transaction, 'latitude', 0)}, {getattr(transaction, 'longitude', 0)})\n"
            f"Timestamp:        {getattr(transaction, 'timestamp', 'N/A')}\n"
            f"Risk Score:       {getattr(eval_result, 'total_score', 0)} / 100 (HIGH RISK)\n"
            f"Status:           PENDING REVIEW\n\n"
            f"Triggered Rules:\n"
            f"{rules_text}\n"
            f"==================================================\n"
            f"Please investigate this transaction in the Fraud Review Console."
        )

        # 1. If AWS SNS is configured with valid credentials, attempt boto3 dispatch
        if self.is_aws_configured():
            try:
                import boto3
                sns_client = boto3.client(
                    "sns",
                    region_name=self.aws_region,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key
                )
                response = sns_client.publish(
                    TopicArn=self.topic_arn,
                    Subject=subject[:100],  # SNS Subject limit is 100 characters
                    Message=message
                )
                message_id = response.get("MessageId", "UNKNOWN")
                status = f"AWS SNS alert published successfully (MessageId: {message_id})"
                logger.info(status)
                return True, status
            except Exception as e:
                err_msg = f"AWS SNS delivery failed: {str(e)}"
                logger.error(err_msg)
                # Graceful fallback: Do not fail the transaction
                return False, err_msg

        # 2. Offline / Local Demo fallback mode
        fallback_msg = "AWS credentials not configured. High-risk notification logged in Local Demo Simulation Mode."
        logger.warning(
            "\n" + "=" * 60 + "\n"
            + "[LOCAL DEMO SIMULATION] High-Risk Alert Broadcast:\n"
            + message + "\n"
            + "=" * 60
        )
        return True, fallback_msg


notification_service = NotificationService()
