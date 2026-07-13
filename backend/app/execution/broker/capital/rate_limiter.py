"""
Capital.com Rate Limiter

Token-bucket / rolling-window hybrid for Capital.com REST API.
"""
import asyncio
import logging
import time
from typing import List

logger = logging.getLogger(__name__)


class CapitalRateLimiter:
    """
    Token-bucket rate limiter for Capital.com REST API.

    Capital.com documented limits (per app key):
      - 10 requests per second
      - 60 requests per minute
      - 500 requests per 5 minutes
      - 10,000 requests per 24 hours

    We keep a small safety margin below the limits to avoid accidental
    throttling or account suspension. The limiter is shared across all
    Capital.com HTTP clients in the process.
    """

    # Safety margins below documented limits
    MAX_PER_SECOND = 8.0
    MAX_PER_MINUTE = 50.0
    MAX_PER_5_MINUTES = 400.0

    def __init__(self):
        self._lock = asyncio.Lock()
        self._second_window: List[float] = []
        self._minute_window: List[float] = []
        self._five_minute_window: List[float] = []

    async def wait(self) -> None:
        """
        Block until it is safe to make another request.
        """
        while True:
            async with self._lock:
                now = time.monotonic()
                self._prune_windows(now)

                if self._is_allowed(now):
                    self._record_request(now)
                    return

                sleep_time = self._time_until_next_slot(now)

            logger.debug(f"Capital.com rate limiter sleeping for {sleep_time:.3f}s")
            await asyncio.sleep(sleep_time)

    def _prune_windows(self, now: float) -> None:
        self._second_window = [t for t in self._second_window if now - t < 1.0]
        self._minute_window = [t for t in self._minute_window if now - t < 60.0]
        self._five_minute_window = [t for t in self._five_minute_window if now - t < 300.0]

    def _is_allowed(self, now: float) -> bool:
        return (
            len(self._second_window) < self.MAX_PER_SECOND
            and len(self._minute_window) < self.MAX_PER_MINUTE
            and len(self._five_minute_window) < self.MAX_PER_5_MINUTES
        )

    def _record_request(self, now: float) -> None:
        self._second_window.append(now)
        self._minute_window.append(now)
        self._five_minute_window.append(now)

    def _time_until_next_slot(self, now: float) -> float:
        """Return the shortest time until any window frees a slot."""
        candidates = []
        if len(self._second_window) >= self.MAX_PER_SECOND and self._second_window:
            candidates.append(1.0 - (now - self._second_window[0]))
        if len(self._minute_window) >= self.MAX_PER_MINUTE and self._minute_window:
            candidates.append(60.0 - (now - self._minute_window[0]))
        if len(self._five_minute_window) >= self.MAX_PER_5_MINUTES and self._five_minute_window:
            candidates.append(300.0 - (now - self._five_minute_window[0]))

        if not candidates:
            return 0.1
        return max(min(candidates), 0.01)
