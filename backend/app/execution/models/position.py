"""
Aegis Trading System - Execution Position Model
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from app.execution.models.order import OrderDirection


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class Position:
    """
    Represents an open or closed position in the market.
    Maintained by the broker and the Execution Engine.
    """
    position_id: str
    symbol: str
    direction: OrderDirection
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    status: PositionStatus
    opened_at: datetime
    closed_at: Optional[datetime] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    
    # Strategy attribution
    strategy_name: str = "Unknown"
    ranking_score: Decimal = Decimal("0")
    market_regime: str = "Unknown"
    entry_reason: str = "Unknown"

    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized PnL based on current price."""
        if self.status == PositionStatus.CLOSED:
            return Decimal("0")
            
        if self.direction == OrderDirection.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity

    @property
    def unrealized_pnl_percent(self) -> Decimal:
        """Calculate unrealized PnL percentage."""
        if self.entry_price == 0 or self.status == PositionStatus.CLOSED:
            return Decimal("0")
            
        if self.direction == OrderDirection.LONG:
            return (self.current_price - self.entry_price) / self.entry_price * 100
        else:
            return (self.entry_price - self.current_price) / self.entry_price * 100
