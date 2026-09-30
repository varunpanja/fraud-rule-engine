import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Fraud Rule Engine & Review Console"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./fraud_engine.db"
    
    # Fraud Detection Thresholds
    VELOCITY_WINDOW_MINUTES: int = 5
    VELOCITY_MAX_TRANSACTIONS: int = 5
    VELOCITY_SCORE: int = 30
    
    UNUSUAL_AMOUNT_THRESHOLD: float = 100000.0
    AMOUNT_SCORE: int = 30
    
    MAX_REALISTIC_SPEED_KMPH: float = 900.0
    GEO_SCORE: int = 40
    
    HIGH_RISK_THRESHOLD: int = 70
    MEDIUM_RISK_THRESHOLD: int = 30
    
    # AWS SNS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SNS_TOPIC_ARN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
