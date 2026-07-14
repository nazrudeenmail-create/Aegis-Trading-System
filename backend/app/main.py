"""Aegis Trading System - Application Entry Point"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.api.router import api_router

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


def print_startup_banner():
    """Print a safety banner on startup showing broker, mode, and endpoint."""
    border = "=" * 50
    dash = "-" * 50
    print(f"\n{border}")
    print(f"  {settings.APP_NAME}")
    print(dash)
    print(f"  Version     : ATS {settings.APP_VERSION}")
    print(f"  Environment : {settings.APP_ENV}")
    print(f"  Broker      : {settings.broker_display_name}")
    print(f"  Mode        : {settings.account_mode_display}")
    print(f"  Endpoint    : {settings.capital_api_url}")
    print(f"  Database    : {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print(f"{border}\n")


@asynccontextmanager
async def lifespan(application: FastAPI):
    print_startup_banner()
    logger.info("ATS backend starting | env=%s | version=%s", settings.APP_ENV, settings.APP_VERSION)
    from app.core.config_validator import validate_configuration
    validate_configuration()
    from app.analytics.events import event_bus, SystemLogEvent
    from app.api.v1.websocket import init_websocket_broadcaster
    from app.api.dependencies import get_broker_manager
    from app.market.broker_factory import BrokerFactory
    from app.market.calendar.session_manager import SessionManager
    from app.core.state import global_state, SystemState
    from app.analytics.journal import DecisionJournal
    from app.market_analysis.mtf_service import MultiTimeframeService
    from app.strategy.ranking_engine import StrategyRankingEngine
    from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
    from app.strategy.strategies.mtf_trend_alignment import MultiTimeframeTrendAlignmentStrategy
    from app.strategy.strategies.donchian_breakout import DonchianChannelBreakoutStrategy
    from app.risk.engine import RiskEngine
    from app.execution.engine import ExecutionEngine

    init_websocket_broadcaster(event_bus)
    global_state.session_manager = SessionManager(event_bus)
    global_state.event_bus = event_bus
    global_state.journal = DecisionJournal(event_bus)
    global_state.market_service = MultiTimeframeService()
    global_state.ranking_engine = StrategyRankingEngine(strategies=[EMATrendPullbackStrategy(), MultiTimeframeTrendAlignmentStrategy(), DonchianChannelBreakoutStrategy()])
    global_state.risk_engine = RiskEngine()
    global_state.system_state = SystemState()
    
    from app.analytics.telemetry import TelemetryService
    global_state.telemetry = TelemetryService(event_bus)
    global_state.telemetry.heartbeat("Broker", "Initializing")
    global_state.telemetry.heartbeat("MarketData", "Initializing")
    
    # Example: Record a system log that we started
    event_bus.publish(SystemLogEvent(level="INFO", source="System", message="Engines initialized"))

    # ── Infrastructure Layer: Create broker and provider via BrokerFactory ──
    broker_manager = get_broker_manager()
    global_state.broker_manager = broker_manager

    # Use BrokerFactory to create the broker (selects demo/live URL automatically)
    capital_broker = BrokerFactory.create_broker()
    broker_manager.set_active_broker(capital_broker, settings.account_mode_display)
    await broker_manager.connect()
    logger.info(f"Broker connected: {settings.broker_display_name} ({settings.account_mode_display})")

    global_state.execution_engine = ExecutionEngine(broker_manager=broker_manager, risk_engine=global_state.risk_engine, event_bus=event_bus)

    from app.workers.orchestrator import SystemOrchestrator
    from app.workers.market_data_engine import MarketDataEngine
    from app.market.synchronizer import DataSynchronizer
    
    # 1. Start Market Data Engine — use BrokerFactory to get the provider
    synchronizer = DataSynchronizer(event_bus=event_bus)
    market_provider = BrokerFactory.create_provider()
    market_data_engine = MarketDataEngine(
        event_bus=event_bus,
        provider=market_provider,
        synchronizer=synchronizer,
        poll_interval_seconds=60
    )
    await market_data_engine.start()
    
    # 2. Start System Orchestrator
    orchestrator = SystemOrchestrator(
        event_bus=event_bus, 
        session_manager=global_state.session_manager, 
        market_service=global_state.market_service, 
        ranking_engine=global_state.ranking_engine, 
        risk_engine=global_state.risk_engine, 
        execution_engine=global_state.execution_engine, 
        broker_manager=broker_manager, 
        poll_interval_seconds=60
    )
    await orchestrator.start()
    logger.info("SystemOrchestrator background loop started")

    yield
    logger.info("ATS shutting down...")
    await orchestrator.stop()
    await market_data_engine.stop()
    logger.info("ATS backend shut down.")

def create_application() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description="Professional rule-based algorithmic trading platform.", lifespan=lifespan, docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")
    application.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    application.include_router(api_router)
    return application

app = create_application()

@app.get("/health", tags=["Health"])
async def health_root():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION, "environment": settings.APP_ENV}