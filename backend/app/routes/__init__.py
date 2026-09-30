from app.routes.transactions import router as transactions_router
from app.routes.fraud import router as fraud_router
from app.routes.dashboard import router as dashboard_router
from app.routes.demo import router as demo_router

__all__ = ["transactions_router", "fraud_router", "dashboard_router", "demo_router"]
