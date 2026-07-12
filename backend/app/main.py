"""
Aegis Trading System — Application Entry Point

Responsibility:
    - Create and configure the FastAPI application instance.
    - Register all API routers.
    - Configure middleware (CORS).
    - Handle application startup and shutdown lifecycle.
    - Expose the health check endpoint at root level (for Docker health checks).

This file must not contain:
    - Trading logic
    - Database queries
    - Indicator calculations
    - Strategy decisions
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.api.router import api_router

# Initialize logging before anything else.
setup_logging()

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Application lifespan handler (modern FastAPI pattern).

    Replaces deprecated @app.on_event("startup") / @app.on_event("shutdown").

    Code before `yield` runs on startup.
    Code after `yield` runs on shutdown.

    Future phases will add:
        Startup:
            - Database connection pool verification (Phase 2)
            - Market data worker startup (Phase 3)
            - WebSocket manager initialization (Phase 10)
        Shutdown:
            - Graceful worker shutdown (Phase 3+)
            - Open position safety checks before shutdown (Phase 12)
    """
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info(
        "ATS backend starting | env=%s | version=%s",
        settings.APP_ENV,
        settings.APP_VERSION,
    )
    
    from app.core.config_validator import validate_configuration
    validate_configuration()

    from app.analytics.events import event_bus, SystemLogEvent
    from app.api.v1.websocket import init_websocket_broadcaster
    from app.api.dependencies import get_broker_manager
    from app.execution.broker.capital.broker import CapitalComBroker
    from app.market.calendar.session_manager import SessionManager
    from app.core.state import global_state
    
    from app.analytics.journal import DecisionJournal
    from app.market_analysis.mtf_service import MultiTimeframeService
    from app.strategy.ranking_engine import StrategyRankingEngine
    from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
    from app.strategy.strategies.mtf_trend_alignment import MultiTimeframeTrendAlignmentStrategy
    from app.strategy.strategies.donchian_breakout import DonchianChannelBreakoutStrategy
    from app.risk.engine import RiskEngine
    from app.execution.engine import ExecutionEngine
    from app.execution.broker.paper.broker import PaperBroker
    from app.execution.models.paper_config import ExecutionSimulationConfig
    
    init_websocket_broadcaster(event_bus)
    
    global_state.session_manager = SessionManager(event_bus)
    global_state.event_bus = event_bus
    global_state.journal = DecisionJournal(event_bus)
    global_state.market_service = MultiTimeframeService()
    global_state.strategy_engine = None # Deprecated? We use ranking_engine now
    global_state.ranking_engine = StrategyRankingEngine(
        strategies=[
            EMATrendPullbackStrategy(),
            MultiTimeframeTrendAlignmentStrategy(),
            DonchianChannelBreakoutStrategy()
        ]
    )
    global_state.risk_engine = RiskEngine()
    
    event_bus.publish(SystemLogEvent(level="INFO", source="System", message="Decision Journal initialized"))
    event_bus.publish(SystemLogEvent(level="INFO", source="System", message="Strategy Engine initialized"))
    event_bus.publish(SystemLogEvent(level="INFO", source="System", message="Risk Engine initialized"))
    
    broker_manager = get_broker_manager()
    global_state.broker_manager = broker_manager
    from decimal import Decimal

    # Initialize Execution Environment
    # Always create paper broker for the router
    paper_broker = PaperBroker(initial_balance=Decimal("100000.0"), config=ExecutionSimulationConfig())

    if settings.GLOBAL_TRADING_MODE in ["BROKER_DEMO", "BROKER_LIVE"]:
        capital_broker = CapitalComBroker(
            api_key=settings.CAPITAL_COM_API_KEY,
            identifier=settings.CAPITAL_COM_USERNAME,
            password=settings.CAPITAL_COM_PASSWORD,
            base_url=settings.CAPITAL_COM_API_URL
        )
        broker_manager.set_active_broker(capital_broker, settings.GLOBAL_TRADING_MODE)
        await broker_manager.connect()
    else:
        broker_manager.set_active_broker(paper_broker, "SIMULATION")
        
    global_state.execution_engine = ExecutionEngine(
        paper_broker=paper_broker,
        broker_manager=broker_manager,
        risk_engine=global_state.risk_engine,
        event_bus=event_bus
    )

    yield  # Application runs here

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("ATS backend shutting down.")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Professional rule-based algorithmic trading platform.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS — allow frontend to communicate with backend.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register all API routes under /api/v1
    application.include_router(api_router)

    return application


app = create_application()


@app.get("/health", tags=["Health"])
async def health_root():
    """
    Root health check endpoint.

    Used by:
        - Docker HEALTHCHECK instruction
        - Kubernetes liveness probes
        - Load balancers

    Returns:
        dict: System status.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
