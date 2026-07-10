from abc import ABC, abstractmethod
from typing import List

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe


class MarketDataProvider(ABC):
    """
    Abstract Base Class for Market Data Providers.
    Ensures all providers implement the required interface.
    """

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the provider and establish a session."""
        pass

    @abstractmethod
    def fetch_historical_candles(
        self, instrument: str, timeframe: Timeframe, limit: int
    ) -> List[Candle]:
        """
        Fetch historical candles from the provider.
        Must return ATS Domain Candle objects.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connection to provider and release resources."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
