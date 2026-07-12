"""
Aegis Trading System - Decision Journal Service
"""

import logging
from typing import Dict, List
from datetime import datetime

from app.analytics.events import EventBus, DecisionEvent, ExecutionEvent, TradeClosedEvent
from app.analytics.models import DecisionRecord, StrategyScoreRecord
from app.strategy.models.ranking import RankingResult
from app.risk.models import RiskAssessment

logger = logging.getLogger(__name__)

class DecisionJournal:
    """
    Records the "why" behind every trading decision immutably.
    Links decisions to their execution outcomes.
    """
    def __init__(self, event_bus: EventBus):
        self.decisions: Dict[str, DecisionRecord] = {}
        self.trade_to_decision: Dict[str, str] = {} # trade_id -> decision_id
        
        # Subscribe to events
        event_bus.subscribe(DecisionEvent, self.handle_decision)
        event_bus.subscribe(ExecutionEvent, self.handle_execution)
        event_bus.subscribe(TradeClosedEvent, self.handle_trade_closed)

    def handle_decision(self, event: DecisionEvent):
        """
        Logs a new decision with full strategy ranking and risk context.
        """
        ranking = event.ranking_result
        risk = event.risk_assessment
        
        # Extract strategy competition
        strategies_considered = []
        for rank, score in enumerate(ranking.rankings):
            strategies_considered.append(StrategyScoreRecord(
                strategy_name=score.strategy_name,
                score=score.final_score,
                rank=rank + 1
            ))
            
        selected = ranking.selected_strategy
        
        # Extract specific scores if a strategy was selected
        hist_score, comp_score, set_score, final_score = None, None, None, None
        if selected:
            for s in ranking.rankings:
                if s.strategy_name == selected:
                    hist_score = s.historical_score
                    comp_score = s.market_score
                    set_score = s.setup_score
                    final_score = s.final_score
                    break
        
        record = DecisionRecord(
            decision_id=event.decision_id,
            timestamp=ranking.timestamp,
            symbol=event.symbol,
            timeframe=event.timeframe,
            market_regime=ranking.market_regime.value if ranking.market_regime else "UNKNOWN",
            strategies_considered=strategies_considered,
            selected_strategy=selected,
            historical_score=hist_score,
            compatibility_score=comp_score,
            setup_score=set_score,
            final_score=final_score,
            confidence_score=set_score, # For simplicity, setup_score represents confidence here
            risk_approved=risk.is_approved if risk else False,
            risk_reason=risk.rejection_reason if risk and not risk.is_approved else None,
            outcome_status="REJECTED" if (not selected or (risk and not risk.is_approved)) else "PENDING"
        )
        
        self.decisions[record.decision_id] = record
        logger.debug(f"Journaled Decision {record.decision_id}: {selected if selected else 'NO_TRADE'}")

    def handle_execution(self, event: ExecutionEvent):
        """
        Links a successful broker order to the decision.
        """
        record = self.decisions.get(event.decision_id)
        if record:
            update_data = {"order_id": event.order_result.order_id}
            if event.order_result.status.value in ["REJECTED", "CANCELLED"]:
                update_data["outcome_status"] = "EXECUTION_FAILED"
            else:
                update_data["outcome_status"] = "EXECUTED"
            
            self.decisions[event.decision_id] = record.model_copy(update=update_data)

    def handle_trade_closed(self, event: TradeClosedEvent):
        """
        Links a closed trade outcome back to the original decision.
        """
        trade = event.trade_record
        
        target_decision = None
        for decision in self.decisions.values():
            if decision.order_id == trade.trade_id:
                target_decision = decision
                break
                
        if target_decision:
            update_data = {
                "trade_id": trade.trade_id,
                "profit_loss": trade.pnl,
                "r_multiple": trade.pnl_percent / 100.0  # simplified R for MVP
            }
            
            if trade.pnl > 0:
                update_data["outcome_status"] = "WIN"
            elif trade.pnl < 0:
                update_data["outcome_status"] = "LOSS"
            else:
                update_data["outcome_status"] = "BREAK_EVEN"
                
            self.decisions[target_decision.decision_id] = target_decision.model_copy(update=update_data)
            logger.debug(f"Decision {target_decision.decision_id} resulted in {update_data['outcome_status']} ({trade.pnl})")

    def get_all_decisions(self) -> List[DecisionRecord]:
        return list(self.decisions.values())
