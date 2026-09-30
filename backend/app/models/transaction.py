from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR", nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(String(128), nullable=False)
    transaction_type = Column(String(32), default="TRANSFER", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    fraud_flag = relationship("FraudFlag", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
