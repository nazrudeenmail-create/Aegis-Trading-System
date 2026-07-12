"""
Aegis Trading System - Analytics Event Bus
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from app.strategy.models.ranking import RankingResult
from app.risk.models import RiskAssessment
from app.execution.models.order import OrderResult, TradeRecord


class Event:
    pass


@dataclass
class DecisionEvent(Event):
    """
    Emitted when the Strategy Ranking Engine has made a selection
    and the Risk Engine has evaluated it.
    """
    decision_id: str
    symbol: str
    timeframe: str
    ranking_result: RankingResult
    risk_assessment: RiskAssessment


@dataclass
class ExecutionEvent(Event):
    """
    Emitted when an order has been placed with the broker.
    """
    decision_id: str
    order_result: OrderResult


@dataclass
class TradeClosedEvent(Event):
    """
    Emitted when a position is completely closed.
    """
    trade_record: TradeRecord


class EventBus:
    """
    Simple synchronous event bus for decoupling execution from analytics.
    In a real production environment (Phase 13), this could be backed by Redis or RabbitMQ.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: type, handler: Callable[[Event], None]):
        event_name = event_type.__name__
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(handler)

    def publish(self, event: Event):
        event_name = event.__class__.__name__
        handlers = self.subscribers.get(event_name, [])
        for handler in handlers:
            handler(event)

# Global Event Bus
event_bus = EventBus()
