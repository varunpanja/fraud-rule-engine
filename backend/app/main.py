import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.models import Transaction, FraudFlag  # Ensures models are registered with Base metadata
from app.routes import (
    transactions_router,
    fraud_router,
    dashboard_router,
    demo_router,
)

# Configure logging format
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fraud_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
    yield
    logger.info("Shutting down Fraud Rule Engine application.")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Fraud Detection & Rule Evaluation Engine with React Reviewer Console

### Core Architecture Capabilities:
- **Real-time Rule Evaluation**: Ingests transactions and scores risk against independent rules.
- **Extensible Architecture**: Follows Open-Closed Principle (OCP). New rules can be plugged in without engine refactoring.
- **Mandatory Rules Implemented**:
  1. **Transaction Velocity Rule**: Detects burst transaction volume within time windows (+30 score).
  2. **Unusual Transaction Amount Rule**: Flags transactions exceeding configured thresholds (+30 score).
  3. **Impossible Geographical Location Rule**: Computes Haversine distance and speed between consecutive transactions (+40 score).
- **Automated Alerts**: Dispatches AWS SNS notifications for high-risk transactions (Score \(\ge 70\)).
- **Reviewer Console API**: Supports reviewing, clearing, and auditing flagged transactions.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(transactions_router)
app.include_router(fraud_router)
app.include_router(dashboard_router)
app.include_router(demo_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "rules_registered": 3,
        "aws_sns_mode": "ACTIVE" if settings.AWS_SNS_TOPIC_ARN else "LOCAL_SIMULATION"
    }
