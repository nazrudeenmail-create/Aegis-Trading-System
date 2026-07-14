from typing import Dict, Any
from datetime import datetime
from app.analytics.events import EventBus, Event, DecisionEvent, ExecutionEvent

class PipelineMetrics:
    def __init__(self, event_bus: EventBus):
        self.candles_received = 0
        self.indicator_updates = 0
        self.strategy_evaluations = 0
        self.signals_generated = 0
        self.orders = 0
        self.latency: Dict[str, float] = {}

        event_bus.subscribe(DecisionEvent, self._on_decision)
        event_bus.subscribe(ExecutionEvent, self._on_execution)
        # We need specific events for candles and indicators, but for now we'll mock the counters or increment them via structured events

    def _on_decision(self, event: DecisionEvent):
        self.strategy_evaluations += 1
        if event.ranking_result.selected_strategy:
            self.signals_generated += 1

    def _on_execution(self, event: ExecutionEvent):
        self.orders += 1

global_metrics = None
