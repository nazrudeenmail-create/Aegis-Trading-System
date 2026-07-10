from typing import List

from app.database.repositories.candle_repository import CandleRepository
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.timeframe_builder import TimeframeBuilder


class CandleQueryService:
    """
    Service responsible for fulfilling strategy engine requests for market data.
    Retrieves raw 1M truth from the repository and transforms it to the requested timeframe.
    """

    def __init__(self, repository: CandleRepository, builder: TimeframeBuilder = TimeframeBuilder()):
        self.repository = repository
        self.builder = builder

    def get_latest(self, instrument: str, timeframe: Timeframe, limit: int) -> List[Candle]:
        """
        Retrieves the latest aggregated candles for the requested timeframe.
        Calculates how many 1M candles are needed, fetches them, and aggregates.
        """
        # Calculate exactly how many 1M candles we need to satisfy the request
        # Timeframe.M1 returns 1, Timeframe.H1 returns 60, etc.
        minutes_per_candle = TimeframeBuilder._get_minutes_for_timeframe(timeframe)
        
        # Add a small buffer of 10 periods to account for gaps/holidays
        raw_limit = (limit + 10) * minutes_per_candle

        # Fetch the raw 1M truth
        raw_candles = self.repository.get_latest(instrument=instrument, limit=raw_limit)

        if not raw_candles:
            return []

        # Transform to the requested timeframe
        aggregated_candles = self.builder.aggregate(raw_candles, target_timeframe=timeframe)

        # We may have generated slightly more than requested due to the buffer.
        # Return exactly the requested limit (taking the most recent ones).
        return aggregated_candles[-limit:]
