from abc import ABC, abstractmethod
from datetime import datetime

class MarketCalendar(ABC):
    """
    Interface for determining market sessions, open/close hours, and holidays.
    Important for accurate timeframe building (knowing when a session ends).
    """

    @abstractmethod
    def is_market_open(self, instrument: str, timestamp: datetime) -> bool:
        """Returns True if the market is open at the given timestamp."""
        pass

    @abstractmethod
    def get_session_close(self, instrument: str, timestamp: datetime) -> datetime:
        """Returns the closing time of the current or next active session."""
        pass
