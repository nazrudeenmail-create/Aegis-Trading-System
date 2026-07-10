"""
Aegis Trading System — Abstract Market Data Provider

Responsibility:
    Define the interface that all market data providers must implement.
    Concrete implementations are created in Phase 3.

Architecture rule:
    The market module never depends on a specific data source.
    Strategy, Risk, and Execution modules call data_provider methods.
    The actual provider (broker WebSocket, Polygon, simulation) is a
    configuration choice — not hardcoded anywhere.

Future implementations (Phase 3):
    - BrokerFeedProvider: live data from broker WebSocket
    - SimulationProvider: test data for development and testing
    - PolygonProvider: Polygon.io data feed (optional)
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class MarketDataProvider(ABC):
    """
    Abstract base class for all market data providers.

    Any class that provides market data to ATS must implement these methods.
    This ensures the Strategy Engine and Indicator Engine never depend
    on a specific data source.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the data source.

        Raises:
            ConnectionError: If the connection cannot be established.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Cleanly close the connection to the data source.
        """
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if the data provider is currently connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    async def subscribe(self, symbol: str) -> None:
        """
        Subscribe to market data for a specific symbol.

        Args:
            symbol: Trading instrument identifier (e.g. "SPX500", "BTCUSDT").
        """
        pass

    @abstractmethod
    async def unsubscribe(self, symbol: str) -> None:
        """
        Unsubscribe from market data for a specific symbol.

        Args:
            symbol: Trading instrument identifier.
        """
        pass
