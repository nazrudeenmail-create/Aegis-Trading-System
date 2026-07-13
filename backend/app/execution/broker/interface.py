"""
Aegis Trading System — Abstract Broker Interface

Responsibility:
    Define the interface that all broker implementations must follow.
    Concrete implementations are created in Phase 13.

Architecture rule:
    The Strategy Engine and Risk Engine never call a broker directly.
    They emit TradeCandidates. The ExecutionEngine and BrokerManager
    translate those into broker-specific order calls.

Execution modes:
    - BACKTEST -> app.backtest.simulated_broker.SimulatedBroker
    - DEMO     -> CapitalComBroker (demo endpoint)
    - LIVE     -> CapitalComBroker (live endpoint)
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from app.execution.models.order import OrderRequest, OrderResult


class BrokerInterface(ABC):
    """
    Abstract base class for all broker implementations.

    Any broker that ATS connects to must implement these methods.
    This ensures the rest of the system never depends on a specific broker.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the broker.

        Raises:
            ConnectionError: If the broker cannot be reached.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Cleanly close the broker connection.
        """
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if the broker connection is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    async def place_market_order(self, order: OrderRequest) -> OrderResult:
        """
        Submit a market order for immediate execution.

        Args:
            order: OrderRequest with symbol, direction, quantity.

        Returns:
            OrderResult: Result of the order submission including fill data.
        """
        pass

    @abstractmethod
    async def place_limit_order(self, order: OrderRequest) -> OrderResult:
        """
        Submit a limit (pending) order.

        Args:
            order: OrderRequest with symbol, direction, quantity, price.

        Returns:
            OrderResult: Result of the order submission.
        """
        pass

    @abstractmethod
    async def place_stop_order(self, order: OrderRequest) -> OrderResult:
        """
        Submit a stop (pending) order.

        Args:
            order: OrderRequest with symbol, direction, quantity, stop_price.

        Returns:
            OrderResult: Result of the order submission.
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.

        Args:
            order_id: The broker-assigned order identifier.

        Returns:
            bool: True if cancelled successfully, False otherwise.
        """
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Optional[OrderResult]:
        """
        Retrieve the current status of an order from the broker.

        Args:
            order_id: The broker-assigned order identifier.

        Returns:
            OrderResult or None: Latest order status with fill data if available.
        """
        pass

    @abstractmethod
    async def sync_positions(self) -> List[Dict[str, Any]]:
        """
        Fetch and return open positions from the broker.

        Returns:
            List of position dictionaries with broker-native fields.
        """
        pass

    @abstractmethod
    async def get_account_balance(self) -> float:
        """
        Retrieve current account balance.

        Returns:
            float: Available account balance.
        """
        pass
