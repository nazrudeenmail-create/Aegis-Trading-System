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

from app.api.v1 import health

api_router = APIRouter()

# Health check — always available
api_router.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

# Future routers — registered here when ready:
# Phase 10:
# api_router.include_router(market.router, prefix="/api/v1/market", tags=["Market"])
# api_router.include_router(trades.router, prefix="/api/v1/trades", tags=["Trades"])
# api_router.include_router(signals.router, prefix="/api/v1/signals", tags=["Signals"])
# api_router.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
# api_router.include_router(performance.router, prefix="/api/v1/performance", tags=["Performance"])
