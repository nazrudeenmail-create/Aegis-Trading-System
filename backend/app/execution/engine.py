"""Aegis Trading System - Execution Engine"""
from typing import Dict, Optional
from decimal import Decimal
import logging, uuid
from app.strategy.models import TradeCandidate
from app.strategy.models.ranking import RankingResult
from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.execution.broker.manager import BrokerManager
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderResult
from app.core.config import get_settings
from app.core.state import global_state
from app.analytics.events import EventBus, DecisionEvent, ExecutionEvent
from app.execution.readiness import TradingReadiness

logger = logging.getLogger(__name__)


class ExecutionEngine:

    def __init__(self, broker_manager: BrokerManager, risk_engine: RiskEngine, event_bus: EventBus = None):
        self.broker_manager = broker_manager
        self.risk_engine = risk_engine
        self.event_bus = event_bus
        self.readiness = TradingReadiness(broker_manager)

    async def execute(self, candidate: TradeCandidate, ranking_result: RankingResult, risk_profile: RiskProfile, risk_context: Dict, instrument=None, decision_id: str = None) -> Optional[OrderResult]:
        if not decision_id:
            decision_id = str(uuid.uuid4())
        settings = get_settings()

        # Emergency stop / readiness gate
        if global_state.system_state and global_state.system_state.is_halted:
            logger.warning("ExecutionEngine: Rejected. System is HALTED.")
            return None

        readiness = self.readiness.check()
        if not readiness.ready:
            logger.warning(f"ExecutionEngine: Rejected. Readiness failed: {readiness.blocking_reasons}")
            return None

        if instrument:
            if not instrument.trading_enabled:
                logger.warning(f"Execution rejected: Trading disabled for {candidate.symbol}")
                return None
            if candidate.direction.value in ["LONG", "SHORT"] and not instrument.allow_new_positions:
                logger.warning(f"Execution rejected: New positions not allowed for {candidate.symbol}")
                return None
            if not instrument.live_trading_enabled:
                logger.warning(f"Execution rejected: {settings.account_mode_display} disabled for {candidate.symbol}")
                return None

        risk_assessment = self.risk_engine.evaluate(candidate, profile=risk_profile, context=risk_context)
        if self.event_bus:
            self.event_bus.publish(DecisionEvent(decision_id=decision_id, symbol=candidate.symbol, timeframe=candidate.market_conditions.get('timeframe', 'Unknown'), ranking_result=ranking_result, risk_assessment=risk_assessment))
        if not risk_assessment.is_approved:
            logger.warning(f"ExecutionEngine: Rejected. Reason: {risk_assessment.rejection_reason}")
            return None

        direction = OrderDirection.LONG if candidate.direction.value == "LONG" else OrderDirection.SHORT
        order = OrderRequest(symbol=candidate.symbol, direction=direction, order_type=OrderType.MARKET, quantity=risk_assessment.position_size)
        result = await self.broker_manager.place_order(order)
        if self.event_bus:
            self.event_bus.publish(ExecutionEvent(decision_id=decision_id, order_result=result))
        return result
