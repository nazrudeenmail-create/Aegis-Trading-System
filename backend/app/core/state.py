"""
Global Application State

Holds references to the active engines and services so the API layer
can query them without circular dependencies.

IMPORTANT: This file holds ONLY mutable runtime state.
Configuration values (broker, account_mode, URLs) are NOT stored here.
Read them directly from `settings` wherever needed.
"""
from enum import Enum
from typing import Optional
from app.analytics.events import EventBus
from app.analytics.journal import DecisionJournal


class SystemStateEnum(str, Enum):
    """High-level operational state of the trading system."""
    ACTIVE = "ACTIVE"
    HALTED = "HALTED"
    MAINTENANCE = "MAINTENANCE"


class SystemState:
    """
    Runtime trading system state.

    - ACTIVE: normal operation
    - HALTED: emergency stop; reject all orders
    - MAINTENANCE: administrative pause; reject orders
    """
    def __init__(self, state: SystemStateEnum = SystemStateEnum.ACTIVE):
        self.state = state

    @property
    def is_halted(self) -> bool:
        return self.state in (SystemStateEnum.HALTED, SystemStateEnum.MAINTENANCE)

    def halt(self) -> None:
        self.state = SystemStateEnum.HALTED

    def resume(self) -> None:
        self.state = SystemStateEnum.ACTIVE

    def maintenance(self) -> None:
        self.state = SystemStateEnum.MAINTENANCE


class AppState:
    def __init__(self):
        # Runtime state (changes while ATS is running)
        self.mode: str = "OFFLINE"
        self.event_bus: Optional[EventBus] = None
        self.journal: Optional[DecisionJournal] = None
        self.system_state: Optional[SystemState] = None
        self.telemetry: Optional[Any] = None

        # References to engines that will be populated when ATS starts
        self.market_service = None
        self.strategy_engine = None
        self.ranking_engine = None
        self.risk_engine = None
        self.execution_engine = None
        self.broker_manager = None
        self.session_manager = None

global_state = AppState()
