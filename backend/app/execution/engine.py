"""Aegis Trading System - Execution Engine"""
from typing import Dict, Optional
from decimal import Decimal
import logging, uuid
from app.strategy.models import TradeCandidate
from app.strategy.models.ranking import RankingResult
from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.execution.broker.interface import BrokerInterface
from app.execution.broker.manager import BrokerManager
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderResult, OrderStatus
from app.core.state import global_state
from app.analytics.events import EventBus, DecisionEvent, ExecutionEvent

logger = logging.getLogger(__name__)

class ExecutionRouter:
    def __init__(self, paper_broker: BrokerInterface, broker_manager: BrokerManager):
        self.paper_broker = paper_broker
        self.broker_manager = broker_manager

    async def route_order(self, order: OrderRequest, mode: str) -> OrderResult:
        if mode in ["BROKER_DEMO", "BROKER_LIVE"]:
            return await self.broker_manager.place_order(order)
        else:
            raise ValueError(f"Unknown trading mode for routing: {mode}")

class ExecutionEngine:
    def __init__(self, paper_broker: BrokerInterface, broker_manager: BrokerManager, risk_engine: RiskEngine, event_bus: EventBus = None):
        self.router = ExecutionRouter(paper_broker, broker_manager)
        self.risk_engine = risk_engine
        self.event_bus = event_bus

    async def execute(self, candidate: TradeCandidate, ranking_result: RankingResult, risk_profile: RiskProfile, risk_context: Dict, instrument=None, decision_id: str = None) -> Optional[OrderResult]:
        if not decision_id:
            decision_id = str(uuid.uuid4())
        mode = global_state.global_trading_mode
        if instrument:
            if not instrument.trading_enabled:
                logger.warning(f"Execution rejected: Trading disabled for {candidate.symbol}")
                return None
            if candidate.direction.value in ["LONG", "SHORT"] and not instrument.allow_new_positions:
                logger.warning(f"Execution rejected: New positions not allowed for {candidate.symbol}")
                return None
            if mode in ["BROKER_DEMO", "BROKER_LIVE"] and not instrument.live_trading_enabled:
                logger.warning(f"Execution rejected: {mode} disabled for {candidate.symbol}")
                return None
        risk_assessment = self.risk_engine.evaluate(candidate, profile=risk_profile, context=risk_context)
        if self.event_bus:
            self.event_bus.publish(DecisionEvent(decision_id=decision_id, symbol=candidate.symbol, timeframe=candidate.market_conditions.get('timeframe', 'Unknown'), ranking_result=ranking_result, risk_assessment=risk_assessment))
        if not risk_assessment.is_approved:
            logger.warning(f"ExecutionEngine: Rejected. Reason: {risk_assessment.rejection_reason}")
            return None
        direction = OrderDirection.LONG if candidate.direction.value == "LONG" else OrderDirection.SHORT
        order = OrderRequest(symbol=candidate.symbol, direction=direction, order_type=OrderType.MARKET, quantity=risk_assessment.position_size)
        result = await self.router.route_order(order, mode)
        if self.event_bus:
            self.event_bus.publish(ExecutionEvent(decision_id=decision_id, order_result=result))
        return result