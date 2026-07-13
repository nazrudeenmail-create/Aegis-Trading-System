"""
Aegis Trading System — System Orchestrator (Main Loop)

Responsibility:
    The central "heartbeat" of ATS. Continuously polls active instruments,
    feeds market data through the intelligence pipeline, evaluates strategies,
    ranks them, and routes approved trade candidates to the execution engine.

Architecture:
    Session Check → Fetch Data → Market Intelligence → Strategy
    Evaluation → Ranking → Risk Assessment → Execution → Logging

Runs as an asyncio background task managed by the FastAPI lifespan.
"""
import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models.instrument import Instrument
from app.database.enums import InstrumentStatus

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe

from app.market_analysis.mtf_service import MultiTimeframeService

from app.strategy.base import BaseStrategy
from app.strategy.engine import StrategyEngine
from app.strategy.ranking_engine import StrategyRankingEngine
from app.strategy.models import TradeCandidate, StrategyResult

from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile

from app.execution.engine import ExecutionEngine
from app.execution.broker.manager import BrokerManager

from app.market.calendar.session_manager import SessionManager
from app.analytics.events import EventBus, SystemLogEvent

logger = logging.getLogger(__name__)


class SystemOrchestrator:
    """
    Continuously running background orchestrator.
    Polls active instruments, generates signals, and executes orders.
    """

    def __init__(
        self,
        event_bus: EventBus,
        session_manager: SessionManager,
        market_service: MultiTimeframeService,
        ranking_engine: StrategyRankingEngine,
        risk_engine: RiskEngine,
        execution_engine: ExecutionEngine,
        broker_manager: BrokerManager,
        poll_interval_seconds: int = 60,
    ):
        self.event_bus = event_bus
        self.session_manager = session_manager
        self.market_service = market_service
        self.ranking_engine = ranking_engine
        self.risk_engine = risk_engine
        self.execution_engine = execution_engine
        self.broker_manager = broker_manager
        self.poll_interval_seconds = poll_interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the orchestrator loop as an asyncio task."""
        if self._running:
            logger.warning("Orchestrator is already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"SystemOrchestrator started (poll interval: {self.poll_interval_seconds}s)")

    async def stop(self):
        """Gracefully stop the orchestrator loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SystemOrchestrator stopped")

    async def _run_loop(self):
        """Main orchestrator loop. Runs until _running is set to False."""
        self._log_event("INFO", "System", "Orchestrator main loop started")

        while self._running:
            try:
                await self._scan_all_instruments()
            except Exception as e:
                logger.exception(f"Unhandled error in orchestrator scan cycle: {e}")

            await asyncio.sleep(self.poll_interval_seconds)

    async def _scan_all_instruments(self):
        """Fetch all ACTIVE and WATCHLIST instruments and process each one."""
        db: Session = SessionLocal()
        try:
            result = db.execute(
                select(Instrument).where(Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST]))
            )
            instruments = list(result.scalars().all())

            if not instruments:
                self._log_event("DEBUG", "Orchestrator", "No active or watchlist instruments found")
                return

            for instrument in instruments:
                try:
                    await self._process_instrument(instrument, db)
                except Exception as e:
                    logger.exception(
                        f"Failed to process instrument {instrument.symbol}: {e}"
                    )
        finally:
            db.close()

    async def _process_instrument(self, instrument: Instrument, db: Session):
        """
        Complete pipeline for a single instrument:
        Session Check → Fetch → Intelligence → Strategy → Ranking → Risk → Execution
        """
        symbol = instrument.symbol
        self._log_event("DEBUG", "Orchestrator", f"Scanning {symbol}...")

        # ---- Step 1: Session Check ----
        market_open = self.session_manager.is_market_open(instrument.market_type)
        if not market_open:
            self._log_event("DEBUG", "Orchestrator", f"{symbol}: Market closed — analyzing existing data, skipping execution")

        # ---- Step 2: Market Data Fetch ----
        candles = self._fetch_recent_candles(db, symbol)
        if not candles:
            self._log_event("WARNING", "Orchestrator", f"{symbol}: No candle data available")
            return

        # ---- Step 3: Market Intelligence ----
        all_timeframes = [Timeframe.M1, Timeframe.M5, Timeframe.M15, Timeframe.H1, Timeframe.H4, Timeframe.D1]
        try:
            context = self.market_service.build_context(
                base_1m_candles=candles,
                required_timeframes=all_timeframes,
                primary_timeframe=Timeframe.H4,
            )
        except Exception as e:
            self._log_event("ERROR", "MarketAnalysis", f"{symbol}: Intelligence failed: {e}")
            return

        # Cache the full context so /market/current API can serve it
        self.market_service.latest_contexts[symbol] = context

        # ---- Step 3.5: Strategy Evaluation ----
        strategy_results: Dict[str, "StrategyResult"] = {}
        valid_candidates: List[TradeCandidate] = []

        for strategy in self.ranking_engine.strategies:
            try:
                strat_context = self.market_service.build_context(
                    base_1m_candles=candles,
                    required_timeframes=strategy.required_timeframes,
                    primary_timeframe=strategy.primary_timeframe,
                )
                result = strategy.evaluate(strat_context)
                strategy_results[strategy.name] = result
                if result.is_valid and result.candidate:
                    valid_candidates.append(result.candidate)
            except Exception as e:
                logger.error(f"{symbol}: Strategy {strategy.name} evaluation failed: {e}")

        if not strategy_results:
            self._log_event("INFO", "Orchestrator", f"{symbol}: No strategies returned results")
            return

        # ---- Step 4: Strategy Ranking ----
        primary_snapshot = context.snapshots.get(Timeframe.H4) or context.snapshots.get(
            Timeframe.M15
        )
        if not primary_snapshot:
            self._log_event("WARNING", "Orchestrator", f"{symbol}: No primary snapshot for ranking")
            return

        try:
            ranking_result = self.ranking_engine.rank(
                db=db,
                symbol=symbol,
                timeframe="H4",
                snapshot=primary_snapshot,
                strategy_results=strategy_results,
            )
        except Exception as e:
            self._log_event("ERROR", "Ranking", f"{symbol}: Ranking failed: {e}")
            return

        # ---- Step 5 & 6: Execution & Risk (for the winning strategy) ----
        if not ranking_result.selected_strategy:
            self._log_event("INFO", "Orchestrator", f"{symbol}: No strategy selected for execution")
            return

        # Find the winning strategy's TradeCandidate
        winner_candidate: Optional[TradeCandidate] = None
        for candidate in valid_candidates:
            if candidate.strategy_name == ranking_result.selected_strategy:
                winner_candidate = candidate
                break

        if not winner_candidate:
            self._log_event(
                "DEBUG", "Orchestrator",
                f"{symbol}: {ranking_result.selected_strategy} won ranking but produced no valid trade",
            )
            return

        # Skip execution when market is closed (analysis still runs above)
        if not market_open:
            self._log_event(
                "DEBUG", "Orchestrator",
                f"{symbol}: Market closed — skipping execution",
            )
            return

        if not instrument.trading_enabled:
            self._log_event(
                "INFO", "Risk",
                f"{symbol}: Trading is completely disabled for this instrument",
            )
            return

        if not instrument.allow_new_positions:
            self._log_event(
                "INFO", "Risk",
                f"{symbol}: New positions blocked for this instrument",
            )
            return

        # Get current account balance from the active broker
        try:
            account_balance = await self.broker_manager.get_account_balance()
        except Exception:
            account_balance = 100000.0  # fallback

        risk_profile = RiskProfile(
            account_balance=Decimal(str(account_balance)),
        )

        try:
            result = await self.execution_engine.execute(
                candidate=winner_candidate,
                ranking_result=ranking_result,
                risk_profile=risk_profile,
                risk_context={
                    "current_open_risk_fiat": Decimal("0.0"),
                    "daily_loss_fiat": Decimal("0.0"),
                },
                instrument=instrument,
            )
            if result:
                self._log_event(
                    "INFO", "Execution",
                    f"{symbol}: Order executed — {winner_candidate.strategy_name} "
                    f"{winner_candidate.direction.value} @ {winner_candidate.entry_price} "
                    f"Stop: {winner_candidate.stop_loss}",
                )
            else:
                self._log_event(
                    "INFO", "Risk",
                    f"{symbol}: {winner_candidate.strategy_name} rejected by Risk Engine",
                )
        except Exception as e:
            self._log_event("ERROR", "Execution", f"{symbol}: Execution failed: {e}")

    # ---- Helpers ----

    def _fetch_recent_candles(self, db: Session, symbol: str, count: int = 1440) -> List[Candle]:
        """
        Fetch the most recent 1-minute candles from the database.
        1440 candles = 24 hours of 1M data.
        Falls back to generating synthetic candles if DB is empty.
        """
        from app.database.models.candle import Candle as DBCandle

        result = db.execute(
            select(DBCandle)
            .join(DBCandle.instrument)
            .where(Instrument.symbol == symbol)
            .order_by(DBCandle.timestamp.desc())
            .limit(count)
        )
        db_candles = list(result.scalars().all())

        if not db_candles:
            return self._generate_synthetic_candles(symbol, min(count, 200))

        # Convert DB candles to domain candles (chronological order)
        domain_candles: List[Candle] = []
        for c in reversed(db_candles):
            try:
                domain_candles.append(
                    Candle(
                        instrument=symbol,
                        timeframe=Timeframe.M1,
                        timestamp=c.timestamp,
                        open=c.open,
                        high=c.high,
                        low=c.low,
                        close=c.close,
                        volume=c.volume,
                        source="database",
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to convert DB candle for {symbol}: {e}")

        return domain_candles

    def _generate_synthetic_candles(self, symbol: str, count: int = 50) -> List[Candle]:
        """Generate simple synthetic candles when DB has no data."""
        import random

        candles = []
        base_price = 100.0
        now = datetime.now(timezone.utc)

        for i in range(count):
            price_change = random.uniform(-0.5, 0.5)
            open_price = base_price
            close_price = base_price + price_change
            high_price = max(open_price, close_price) * (1 + abs(random.uniform(0, 0.002)))
            low_price = min(open_price, close_price) * (1 - abs(random.uniform(0, 0.002)))
            volume = random.uniform(100, 10000)

            candles.append(
                Candle(
                    instrument=symbol,
                    timeframe=Timeframe.M1,
                    timestamp=now.replace(second=0, microsecond=0),
                    open=Decimal(str(round(open_price, 5))),
                    high=Decimal(str(round(high_price, 5))),
                    low=Decimal(str(round(low_price, 5))),
                    close=Decimal(str(round(close_price, 5))),
                    volume=Decimal(str(round(volume, 2))),
                    source="synthetic",
                )
            )
            base_price = close_price
            now = now.replace(minute=(now.minute - 1) % 60)

        return candles

    def _log_event(self, level: str, source: str, message: str):
        """Publish a system log event and also log locally."""
        log_msg = f"[{source}] {message}"
        if level == "ERROR":
            logger.error(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        elif level == "DEBUG":
            logger.debug(log_msg)
        else:
            logger.info(log_msg)

        try:
            self.event_bus.publish(
                SystemLogEvent(level=level, source=source, message=message)
            )
        except Exception as e:
            logger.debug(f"Failed to publish event: {e}")