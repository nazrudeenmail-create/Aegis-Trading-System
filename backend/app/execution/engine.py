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
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderResult, OrderStatus

from app.analytics.events import EventBus, DecisionEvent, ExecutionEvent

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """
    Coordinates between Strategy Ranking, Risk Engine, and the Broker.
    """
    
    def __init__(self, broker: BrokerInterface, risk_engine: RiskEngine, event_bus: EventBus = None):
        self.broker = broker
        self.risk_engine = risk_engine
        self.event_bus = event_bus

    async def execute(
        self, 
        candidate: TradeCandidate, 
        ranking_result: RankingResult, 
        risk_profile: RiskProfile, 
        risk_context: Dict,
        decision_id: str = None
    ) -> Optional[OrderResult]:
        """
        Takes the winning strategy's candidate, validates it with Risk, and places the order.
        """
        if not decision_id:
            decision_id = str(uuid.uuid4())
            
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
        
        # 3. Send to Broker
        result = await self.broker.place_order(order)
        
        # Emit ExecutionEvent
        if self.event_bus:
            self.event_bus.publish(ExecutionEvent(
                decision_id=decision_id,
                order_result=result
            ))
        
        # 4. If filled, update the position with SL/TP and strategy metadata
        if result.status == OrderStatus.FILLED:
            if hasattr(self.broker, 'positions'):
                pos = self.broker.positions.get(candidate.symbol)
                if pos:
                    pos.stop_loss = candidate.stop_loss
                    pos.take_profit = candidate.take_profit
                    pos.strategy_name = candidate.strategy_name
                    # Find ranking score
                    r_score = 0.0
                    for r in ranking_result.rankings:
                        if r.strategy_name == candidate.strategy_name:
                            r_score = r.final_score
                            break
                    pos.ranking_score = Decimal(str(r_score))
                    pos.market_regime = candidate.market_conditions.get('regime', 'Unknown')
                    pos.entry_reason = f"Rank selected. Risk Approved."

        return result
