import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False)
    risk_score = Column(Integer, nullable=False, default=0)
    risk_level = Column(String(16), nullable=False)  # LOW, MEDIUM, HIGH
    _triggered_rules = Column("triggered_rules", Text, nullable=False, default="[]")
    status = Column(String(16), nullable=False, default="PENDING")  # PENDING, REVIEWED, CLEARED
    reviewer_notes = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    transaction = relationship("Transaction", back_populates="fraud_flag")

    @property
    def triggered_rules(self):
        try:
            return json.loads(self._triggered_rules) if self._triggered_rules else []
        except Exception:
            return []

    @triggered_rules.setter
    def triggered_rules(self, value):
        if isinstance(value, str):
            self._triggered_rules = value
        else:
            self._triggered_rules = json.dumps(value)
