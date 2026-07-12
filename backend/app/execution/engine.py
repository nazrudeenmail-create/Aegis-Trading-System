"""
Aegis Trading System - Execution Engine
"""

from typing import Dict, Optional
from decimal import Decimal
import logging

from app.strategy.models import TradeCandidate
from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.execution.broker.interface import BrokerInterface
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderResult, OrderStatus

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """
    Coordinates between Strategy Ranking, Risk Engine, and the Broker.
    """
    
    def __init__(self, broker: BrokerInterface, risk_engine: RiskEngine):
        self.broker = broker
        self.risk_engine = risk_engine

    async def execute(self, candidate: TradeCandidate, ranking_score: float, risk_profile: RiskProfile, risk_context: Dict) -> Optional[OrderResult]:
        """
        Takes the winning strategy's candidate, validates it with Risk, and places the order.
        """
        # 1. Evaluate with Risk Engine
        risk_assessment = self.risk_engine.evaluate(candidate, profile=risk_profile, context=risk_context)
        
        if not risk_assessment.is_approved:
            logger.warning(f"ExecutionEngine: Trade rejected by RiskEngine. Reason: {risk_assessment.rejection_reason}")
            # Note: The PaperTradingMonitor should probably track this rejection
            return None
            
        # 2. Convert to OrderRequest
        # The TradeCandidate from Phase 5 has `direction` mapped from app.strategy.models.TradeDirection
        # We need to map it to app.execution.models.order.OrderDirection
        direction = OrderDirection.LONG if candidate.direction.value == "LONG" else OrderDirection.SHORT
        
        order = OrderRequest(
            symbol=candidate.symbol,
            direction=direction,
            order_type=OrderType.MARKET, # MVP uses MARKET
            quantity=risk_assessment.position_size,
            # Limits/stops are omitted for MARKET order entry, 
            # but PaperBroker might need them to track SL/TP for the position!
            # Wait, the OrderRequest has `stop_price` for STOP orders, but for MARKET, we don't pass SL/TP.
            # We need to tell the broker the SL/TP for the position!
            # Wait, our BrokerInterface's OrderRequest doesn't have SL/TP fields for the position itself, 
            # only if it's a STOP/LIMIT entry order.
        )
        
        # 3. Send to Broker
        result = await self.broker.place_order(order)
        
        # 4. If filled, update the position with SL/TP and strategy metadata
        # Since PaperBroker is simulated, we can access it directly to set SL/TP.
        # In a real broker, we would send separate STOP/LIMIT orders (Bracket Orders).
        # For this phase, we will check if it's the PaperBroker and attach metadata.
        if result.status == OrderStatus.FILLED:
            if hasattr(self.broker, 'positions'):
                pos = self.broker.positions.get(candidate.symbol)
                if pos:
                    pos.stop_loss = candidate.stop_loss
                    pos.take_profit = candidate.take_profit
                    pos.strategy_name = candidate.strategy_name
                    pos.ranking_score = ranking_score
                    pos.market_regime = candidate.market_conditions.get('regime', 'Unknown')
                    pos.entry_reason = f"Rank {ranking_score} selected"

        return result
