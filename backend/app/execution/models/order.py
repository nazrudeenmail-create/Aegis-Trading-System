"""
Aegis Trading System - Execution Order Models

Responsibility:
    Define order and trade record structures for the Execution Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class OrderDirection(str, Enum):
    """Trade direction."""
    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(str, Enum):
    """Order execution type."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    """Current state of an order."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class OrderRequest:
    """
    Request to place an order.
    """
    symbol: str
    direction: OrderDirection
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None        # Required for LIMIT orders
    stop_price: Optional[Decimal] = None   # Required for STOP orders


@dataclass
class OrderResult:
    """
    Result returned after an order is processed by the broker.
    """
    order_id: str
    status: OrderStatus
    filled_price: Optional[Decimal] = None
    filled_quantity: Optional[Decimal] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.now()


@dataclass
class TradeRecord:
    """
    Record of a completed trade for the Decision Journal and performance analytics.
    """
    trade_id: str
    symbol: str
    direction: OrderDirection
    entry_price: Decimal
    exit_price: Decimal
    quantity: Decimal
    pnl: Decimal
    pnl_percent: Decimal
    entry_time: datetime
    exit_time: datetime
    
    # Strategy Attribution (Phase 9 improvements)
    strategy_name: str
    ranking_score: Decimal
    market_regime: str
    entry_reason: str
    exit_reason: str
