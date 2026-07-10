from typing import List, Dict, Optional, Tuple
import threading

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe


class CandleCache:
    """
    In-memory cache for market data to speed up backtesting and strategy execution.
    Acts as a fast, thread-safe layer above the PostgreSQL repository.
    """

    def __init__(self, max_size: int = 2000):
        # Dictionary structure: { ("EURUSD", "1M"): [Candle, Candle, ...] }
        # Candles are assumed to be sorted chronologically
        self._cache: Dict[Tuple[str, str], List[Candle]] = {}
        self._lock = threading.Lock()
        self.max_size = max_size

    def _get_key(self, instrument: str, timeframe: Timeframe) -> Tuple[str, str]:
        return (instrument, timeframe.value)

    def get(self, instrument: str, timeframe: Timeframe) -> Optional[List[Candle]]:
        """Retrieve candles from cache for a specific instrument and timeframe."""
        with self._lock:
            candles = self._cache.get(self._get_key(instrument, timeframe))
            return list(candles) if candles else None

    def set(self, instrument: str, timeframe: Timeframe, candles: List[Candle]) -> None:
        """Store candles in cache, enforcing eviction limit."""
        with self._lock:
            self._cache[self._get_key(instrument, timeframe)] = candles[-self.max_size:]

    def append(self, instrument: str, timeframe: Timeframe, candle: Candle) -> None:
        """Append a new live candle to the cache, enforcing eviction limit."""
        key = self._get_key(instrument, timeframe)
        with self._lock:
            if key not in self._cache:
                self._cache[key] = []
            self._cache[key].append(candle)
            
            if len(self._cache[key]) > self.max_size:
                self._cache[key] = self._cache[key][-self.max_size:]

    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()
