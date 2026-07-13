"""
Aegis Trading System - Broker Manager
"""
from typing import Optional, Dict, Any, List
import logging
from app.execution.broker.interface import BrokerInterface
from app.execution.models.order import OrderRequest, OrderResult, OrderType
from app.execution.broker.models import ConnectionState

logger = logging.getLogger(__name__)


class BrokerManager:
    """
    Manages the active broker connection. Abstracts the execution engine from
    knowing whether we are using a Demo broker, a Live broker, or which specific broker
    (Capital.com, IBKR, etc.) is currently active.
    """
    def __init__(self):
        self._active_broker: Optional[BrokerInterface] = None
        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.latency_ms: int = 0
        self.reconnects_today: int = 0
        self.environment: str = "Unknown"
        self._cached_positions: List[Dict[str, Any]] = []

    def set_active_broker(self, broker: BrokerInterface, environment: str = "Demo"):
        """Sets the broker instance to be used for routing live/demo orders."""
        self._active_broker = broker
        self.environment = environment

    def get_active_broker(self) -> Optional[BrokerInterface]:
        """Gets the active broker instance."""
        return self._active_broker

    async def connect(self):
        if not self._active_broker:
            logger.error("No active broker set.")
            return
        self.state = ConnectionState.CONNECTING
        try:
            await self._active_broker.connect()
            self.state = ConnectionState.CONNECTED
        except Exception as e:
            logger.error(f"Failed to connect broker: {e}")
            self.state = ConnectionState.ERROR

    async def disconnect(self):
        if self._active_broker:
            await self._active_broker.disconnect()
        self.state = ConnectionState.DISCONNECTED

    async def place_order(self, order: OrderRequest) -> OrderResult:
        if not self._active_broker or self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Cannot place order: Broker disconnected.")

        if order.order_type == OrderType.MARKET:
            return await self._active_broker.place_market_order(order)
        elif order.order_type == OrderType.LIMIT:
            return await self._active_broker.place_limit_order(order)
        elif order.order_type == OrderType.STOP:
            return await self._active_broker.place_stop_order(order)
        else:
            raise ValueError(f"Unsupported order type: {order.order_type}")

    async def cancel_order(self, order_id: str) -> bool:
        if not self._active_broker:
            return False
        return await self._active_broker.cancel_order(order_id)

    async def get_order_status(self, order_id: str) -> Optional[OrderResult]:
        if not self._active_broker:
            return None
        return await self._active_broker.get_order_status(order_id)

    async def sync_positions(self) -> List[Dict[str, Any]]:
        if not self._active_broker:
            return []
        self._cached_positions = await self._active_broker.sync_positions()
        return self._cached_positions

    def get_cached_positions(self) -> List[Dict[str, Any]]:
        return self._cached_positions

    async def get_account_balance(self) -> float:
        if not self._active_broker:
            return 0.0
        return await self._active_broker.get_account_balance()

    async def search_instruments(self, query: str) -> list:
        if not self._active_broker:
            return []

        # If the active broker supports searching, call it
        if hasattr(self._active_broker, 'search_instruments'):
            return await self._active_broker.search_instruments(query)

        return []
