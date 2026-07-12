"""
Aegis Trading System - Broker Models & Events
"""
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass
from typing import Optional
from app.analytics.events import Event


class ConnectionState(str, Enum):
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    AUTHENTICATING = "AUTHENTICATING"
    RECONNECTING = "RECONNECTING"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class BrokerCapabilities(BaseModel):
    """
    Defines the capabilities supported by a specific broker implementation.
    """
    supports_market_orders: bool = True
    supports_limit_orders: bool = True
    supports_stop_orders: bool = True
    supports_trailing_stop: bool = False
    supports_partial_close: bool = False
    supports_margin: bool = False
    supports_hedging: bool = False


# Broker Event Bus models
@dataclass
class BrokerEvent(Event):
    broker_name: str

@dataclass
class BrokerStateChanged(BrokerEvent):
    old_state: ConnectionState
    new_state: ConnectionState

@dataclass
class OrderAccepted(BrokerEvent):
    order_id: str

@dataclass
class OrderFilled(BrokerEvent):
    order_id: str
    fill_price: float
    fill_qty: float

@dataclass
class OrderRejected(BrokerEvent):
    order_id: str
    reason: str

@dataclass
class PositionClosed(BrokerEvent):
    symbol: str
    realized_pnl: float

@dataclass
class MarginWarning(BrokerEvent):
    margin_used_pct: float
    message: str

@dataclass
class BrokerDisconnected(BrokerEvent):
    reason: str
