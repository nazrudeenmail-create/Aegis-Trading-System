"""Aegis Trading System - Application Entry Point"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.api.router import api_router

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("ATS backend starting | env=%s | version=%s", settings.APP_ENV, settings.APP_VERSION)
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
    from decimal import Decimal

    init_websocket_broadcaster(event_bus)
    global_state.session_manager = SessionManager(event_bus)
    global_state.event_bus = event_bus
    global_state.journal = DecisionJournal(event_bus)
    global_state.market_service = MultiTimeframeService()
    global_state.ranking_engine = StrategyRankingEngine(strategies=[EMATrendPullbackStrategy(), MultiTimeframeTrendAlignmentStrategy(), DonchianChannelBreakoutStrategy()])
    global_state.risk_engine = RiskEngine()
    event_bus.publish(SystemLogEvent(level="INFO", source="System", message="Engines initialized"))

    broker_manager = get_broker_manager()
    global_state.broker_manager = broker_manager
    paper_broker = PaperBroker(initial_balance=Decimal("100000.0"), config=ExecutionSimulationConfig())
    capital_broker = CapitalComBroker(api_key=settings.CAPITAL_COM_API_KEY, identifier=settings.CAPITAL_COM_USERNAME, password=settings.CAPITAL_COM_PASSWORD, base_url=settings.CAPITAL_COM_API_URL)
    broker_manager.set_active_broker(capital_broker, settings.GLOBAL_TRADING_MODE)
    await broker_manager.connect()
    logger.info(f"Broker connected: {settings.GLOBAL_TRADING_MODE}")

    global_state.execution_engine = ExecutionEngine(paper_broker=paper_broker, broker_manager=broker_manager, risk_engine=global_state.risk_engine, event_bus=event_bus)

    from app.workers.orchestrator import SystemOrchestrator
    from app.workers.market_data_engine import MarketDataEngine
    from app.market.synchronizer import DataSynchronizer
    from app.market.providers.capital_com_provider import CapitalComProvider
    
    # 1. Start Market Data Engine
    synchronizer = DataSynchronizer(event_bus=event_bus)
    market_provider = CapitalComProvider(
        api_url=settings.CAPITAL_COM_API_URL, api_key=settings.CAPITAL_COM_API_KEY,
        username=settings.CAPITAL_COM_USERNAME, password=settings.CAPITAL_COM_PASSWORD
    )
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