"""
Aegis Trading System - Execution Engine
"""

from typing import Dict, Optional
from decimal import Decimal
import logging
import uuid

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
    """
    Routes orders to the appropriate execution venue (Paper Simulator vs Real Broker)
    based on the current trading mode.
    """
    def __init__(self, paper_broker: BrokerInterface, broker_manager: BrokerManager):
        self.paper_broker = paper_broker
        self.broker_manager = broker_manager

    async def route_order(self, order: OrderRequest, mode: str) -> OrderResult:
        if mode == "SIMULATION":
            return await self.paper_broker.place_order(order)
        elif mode in ["BROKER_DEMO", "BROKER_LIVE"]:
            return await self.broker_manager.place_order(order)
        else:
            raise ValueError(f"Unknown trading mode for routing: {mode}")

class ExecutionEngine:
    """
    Coordinates between Strategy Ranking, Risk Engine, and the Broker.
    """
    
    def __init__(self, paper_broker: BrokerInterface, broker_manager: BrokerManager, risk_engine: RiskEngine, event_bus: EventBus = None):
        self.router = ExecutionRouter(paper_broker, broker_manager)
        self.risk_engine = risk_engine
        self.event_bus = event_bus

    async def execute(
        self, 
        candidate: TradeCandidate, 
        ranking_result: RankingResult, 
        risk_profile: RiskProfile, 
        risk_context: Dict,
        instrument=None,
        decision_id: str = None
    ) -> Optional[OrderResult]:
        """
        Takes the winning strategy's candidate, validates it with Risk, and places the order.
        """
        if not decision_id:
            decision_id = str(uuid.uuid4())
            
        mode = global_state.global_trading_mode

        # 0. Global Mode & Instrument Permission Checks
        if instrument:
            if not instrument.trading_enabled:
                logger.warning(f"Execution rejected: Trading is globally disabled for {candidate.symbol}")
                return None
                
            is_new_position = candidate.direction.value in ["LONG", "SHORT"] 
            if is_new_position and not instrument.allow_new_positions:
                logger.warning(f"Execution rejected: New positions are not allowed for {candidate.symbol}")
                return None
                
            if mode == "SIMULATION" and not instrument.paper_trading_enabled:
                logger.warning(f"Execution rejected: SIMULATION mode but paper_trading_enabled=False for {candidate.symbol}")
                return None
            if mode in ["BROKER_DEMO", "BROKER_LIVE"] and not instrument.live_trading_enabled:
                logger.warning(f"Execution rejected: {mode} mode but live_trading_enabled=False for {candidate.symbol}")
                return None
                
        # 1. Evaluate with Risk Engine
        risk_assessment = self.risk_engine.evaluate(candidate, profile=risk_profile, context=risk_context)
        
        # Emit DecisionEvent
        if self.event_bus:
            self.event_bus.publish(DecisionEvent(
                decision_id=decision_id,
                symbol=candidate.symbol,
                timeframe=candidate.market_conditions.get('timeframe', 'Unknown'),
                ranking_result=ranking_result,
                risk_assessment=risk_assessment
            ))
        
        if not risk_assessment.is_approved:
            logger.warning(f"ExecutionEngine: Trade rejected by RiskEngine. Reason: {risk_assessment.rejection_reason}")
            return None
            
        # 2. Convert to OrderRequest
        direction = OrderDirection.LONG if candidate.direction.value == "LONG" else OrderDirection.SHORT
        
        order = OrderRequest(
            symbol=candidate.symbol,
            direction=direction,
            order_type=OrderType.MARKET,
            quantity=risk_assessment.position_size,
        )
        
        # 3. Send to Router
        result = await self.router.route_order(order, mode)
        
        # Emit ExecutionEvent
        if self.event_bus:
            self.event_bus.publish(ExecutionEvent(
                decision_id=decision_id,
                order_result=result
            ))

        return result
