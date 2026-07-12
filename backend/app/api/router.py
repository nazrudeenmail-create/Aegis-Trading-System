"""
Aegis Trading System — Central API Router

Responsibility:
    - Register all versioned API routers in one place.
    - Apply the /api/v1 prefix to all routes.
    - Keep main.py clean — it only calls include_router(api_router).

Adding a new domain router (example — Phase 10):
    from app.api.v1 import market
    api_router.include_router(market.router, prefix="/market", tags=["Market"])
"""

from fastapi import APIRouter

from app.api.v1 import health, system, market, strategy, journal, websocket, instruments, dashboard, broker, risk, pipeline

api_router = APIRouter()

# Health check — always available
api_router.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

# Phase 11 Endpoints
api_router.include_router(websocket.router, prefix="/api/v1", tags=["WebSockets"])
api_router.include_router(system.router, prefix="/api/v1/system", tags=["System"])
api_router.include_router(market.router, prefix="/api/v1/market", tags=["Market"])
api_router.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
api_router.include_router(journal.router, prefix="/api/v1/journal", tags=["Journal"])
api_router.include_router(instruments.router, prefix="/api/v1", tags=["Instruments"])
api_router.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
api_router.include_router(broker.router, prefix="/api/v1", tags=["Broker"])
api_router.include_router(risk.router, prefix="/api/v1", tags=["Risk"])
api_router.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
