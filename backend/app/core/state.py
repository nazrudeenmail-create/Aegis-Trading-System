"""
Global Application State

Holds references to the active engines and services so the API layer
can query them without circular dependencies.
"""
from typing import Optional
from app.analytics.events import EventBus
from app.analytics.journal import DecisionJournal

class AppState:
    def __init__(self):
        self.mode: str = "OFFLINE"
        self.event_bus: Optional[EventBus] = None
        self.journal: Optional[DecisionJournal] = None
        
        # References to engines that will be populated when ATS starts
        self.market_service = None
        self.strategy_engine = None
        self.ranking_engine = None
        self.risk_engine = None
        self.execution_engine = None
        self.paper_broker = None

global_state = AppState()
