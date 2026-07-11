"""
Aegis Trading System — Abstract Broker Interface

Responsibility:
    Define the interface that all broker implementations must follow.
    Concrete implementations are created in Phase 12.

Architecture rule:
    The Strategy Engine and Risk Engine never call a broker directly.
    They call broker_interface methods. The actual broker is a
    configuration choice — not hardcoded anywhere.

Future implementations (Phase 12):
    - PaperBroker: simulated execution for paper trading (first implementation)
    - IBKRBroker: Interactive Brokers live trading
    - AlpacaBroker: Alpaca live trading
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
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

    Created by the Execution Engine after Risk approval.
    Sent to the broker interface for execution.
    """
    symbol: str
    direction: OrderDirection
    order_type: OrderType
    quantity: float
    price: Optional[float] = None        # Required for LIMIT orders
    stop_price: Optional[float] = None   # Required for STOP orders


@dataclass
class OrderResult:
    """
    Result returned after an order is processed by the broker.
    """
    order_id: str
    status: OrderStatus
    filled_price: Optional[float] = None
    filled_quantity: Optional[float] = None
    message: Optional[str] = None


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
    async def place_order(self, order: OrderRequest) -> OrderResult:
        """
        Submit an order to the broker.

        Args:
            order: OrderRequest with symbol, direction, quantity, type.

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
    async def get_account_balance(self) -> float:
        """
        Retrieve current account balance.

        Returns:
            float: Available account balance.
        """
        pass
