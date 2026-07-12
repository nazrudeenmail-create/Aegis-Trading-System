"""
Aegis Trading System - Paper Broker Implementation
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import uuid

from app.execution.broker.interface import BrokerInterface
from app.execution.models.order import (
    OrderRequest, OrderResult, OrderStatus, OrderType, OrderDirection, TradeRecord
)
from app.execution.models.position import Position, PositionStatus
from app.execution.models.paper_config import ExecutionSimulationConfig


class PaperBroker(BrokerInterface):
    """
    Simulates a live broker for paper trading.
    Maintains internal balance, positions, and simulates fills with slippage/commissions.
    """
    def __init__(self, initial_balance: Decimal, config: ExecutionSimulationConfig, event_bus=None):
        self.balance = initial_balance
        self.config = config
        self.is_active = False
        self.event_bus = event_bus
        
        # State
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.closed_trades: List[TradeRecord] = []
        
        # We need the current price to fill MARKET orders instantly
        # In a real system, the broker knows the price. Here, we must inject it via tick()
        self.latest_prices: Dict[str, Decimal] = {}
        self.latest_timestamps: Dict[str, datetime] = {}

    async def connect(self) -> None:
        self.is_active = True
        
    async def disconnect(self) -> None:
        self.is_active = False
        
    async def is_connected(self) -> bool:
        return self.is_active

    async def place_order(self, order: OrderRequest) -> OrderResult:
        if not self.is_active:
            raise ConnectionError("Broker is disconnected.")
            
        if self.config.execution_delay_ms > 0:
            await asyncio.sleep(self.config.execution_delay_ms / 1000.0)

        # For this phase, we only support MARKET orders for instant fill
        if order.order_type != OrderType.MARKET:
            return OrderResult(
                order_id=str(uuid.uuid4()),
                status=OrderStatus.REJECTED,
                message="PaperBroker currently only supports MARKET orders."
            )
            
        symbol = order.symbol
        if symbol not in self.latest_prices:
            return OrderResult(
                order_id=str(uuid.uuid4()),
                status=OrderStatus.REJECTED,
                message=f"No price data available for {symbol}"
            )
            
        current_price = self.latest_prices[symbol]
        timestamp = self.latest_timestamps[symbol]
        
        # Apply Slippage
        fill_price = current_price
        if self.config.slippage_enabled:
            slippage_amt = current_price * self.config.slippage_percentage
            if order.direction == OrderDirection.LONG:
                fill_price += slippage_amt
            else:
                fill_price -= slippage_amt
                
        # Deduct Commission
        commission = Decimal("0")
        if self.config.commission_enabled:
            commission = self.config.commission_rate
            self.balance -= commission

        # Position Netting Logic
        existing_pos = self.positions.get(symbol)
        
        if existing_pos and existing_pos.status == PositionStatus.OPEN:
            # Check if this is a closing order
            if existing_pos.direction != order.direction:
                if existing_pos.quantity == order.quantity:
                    # Full close
                    return self._close_position(existing_pos, fill_price, timestamp)
                else:
                    # Partial close or reverse not supported in simple MVP
                    return OrderResult(
                        order_id=str(uuid.uuid4()),
                        status=OrderStatus.REJECTED,
                        message="Partial close or position reversal not supported in MVP."
                    )
            else:
                # Add to position
                return OrderResult(
                    order_id=str(uuid.uuid4()),
                    status=OrderStatus.REJECTED,
                    message="Pyramiding (adding to existing position) not supported in MVP."
                )
        else:
            # Open new position
            new_pos = Position(
                position_id=str(uuid.uuid4()),
                symbol=symbol,
                direction=order.direction,
                quantity=order.quantity,
                entry_price=fill_price,
                current_price=fill_price,
                status=PositionStatus.OPEN,
                opened_at=timestamp
            )
            self.positions[symbol] = new_pos
            
            return OrderResult(
                order_id=new_pos.position_id,
                status=OrderStatus.FILLED,
                filled_price=fill_price,
                filled_quantity=order.quantity,
                timestamp=timestamp
            )

    async def cancel_order(self, order_id: str) -> bool:
        # Since we instantly fill MARKET orders, there are no pending orders to cancel
        return False

    async def get_account_balance(self) -> float:
        # Returns balance plus unrealized PnL
        unrealized = sum(p.unrealized_pnl for p in self.positions.values() if p.status == PositionStatus.OPEN)
        return float(self.balance + unrealized)
        
    def tick(self, symbol: str, price: Decimal, timestamp: datetime):
        """
        Update the broker's market prices. 
        In a real system, the broker has its own feed. Here, the engine feeds it.
        This allows checking for Stop Loss / Take Profit hits.
        """
        self.latest_prices[symbol] = price
        self.latest_timestamps[symbol] = timestamp
        
        # Check open positions for SL/TP
        pos = self.positions.get(symbol)
        if pos and pos.status == PositionStatus.OPEN:
            pos.current_price = price
            
            if pos.direction == OrderDirection.LONG:
                if pos.stop_loss and price <= pos.stop_loss:
                    self._close_position(pos, pos.stop_loss, timestamp, exit_reason="STOP_LOSS")
                elif pos.take_profit and price >= pos.take_profit:
                    self._close_position(pos, pos.take_profit, timestamp, exit_reason="TAKE_PROFIT")
            else: # SHORT
                if pos.stop_loss and price >= pos.stop_loss:
                    self._close_position(pos, pos.stop_loss, timestamp, exit_reason="STOP_LOSS")
                elif pos.take_profit and price <= pos.take_profit:
                    self._close_position(pos, pos.take_profit, timestamp, exit_reason="TAKE_PROFIT")

    def _close_position(self, pos: Position, fill_price: Decimal, timestamp: datetime, exit_reason: str = "MARKET_CLOSE") -> OrderResult:
        # Apply exit slippage
        if self.config.slippage_enabled:
            slippage_amt = fill_price * self.config.slippage_percentage
            if pos.direction == OrderDirection.LONG: # Selling to close
                fill_price -= slippage_amt
            else: # Buying to close
                fill_price += slippage_amt
                
        # Exit commission
        commission = Decimal("0")
        if self.config.commission_enabled:
            commission = self.config.commission_rate
            self.balance -= commission

        pos.status = PositionStatus.CLOSED
        pos.closed_at = timestamp
        pos.current_price = fill_price

        # Calculate PnL
        if pos.direction == OrderDirection.LONG:
            pnl = (fill_price - pos.entry_price) * pos.quantity
            pnl_percent = (fill_price - pos.entry_price) / pos.entry_price * 100
        else:
            pnl = (pos.entry_price - fill_price) * pos.quantity
            pnl_percent = (pos.entry_price - fill_price) / pos.entry_price * 100
            
        self.balance += pnl
        
        # Create TradeRecord
        record = TradeRecord(
            trade_id=pos.position_id, # Link trade_id directly to the position/order ID to match decision link
            symbol=pos.symbol,
            direction=pos.direction,
            entry_price=pos.entry_price,
            exit_price=fill_price,
            quantity=pos.quantity,
            pnl=pnl,
            pnl_percent=pnl_percent,
            entry_time=pos.opened_at,
            exit_time=timestamp,
            strategy_name=pos.strategy_name,
            ranking_score=pos.ranking_score,
            market_regime=pos.market_regime,
            entry_reason=pos.entry_reason,
            exit_reason=exit_reason
        )
        self.closed_trades.append(record)
        del self.positions[pos.symbol]
        
        # Emit TradeClosedEvent
        if hasattr(self, 'event_bus') and self.event_bus:
            from app.analytics.events import TradeClosedEvent
            self.event_bus.publish(TradeClosedEvent(trade_record=record))
        
        return OrderResult(
            order_id=str(uuid.uuid4()),
            status=OrderStatus.FILLED,
            filled_price=fill_price,
            filled_quantity=pos.quantity,
            timestamp=timestamp
        )
        
    def get_closed_trades(self) -> List[TradeRecord]:
        return self.closed_trades
