from typing import List
from decimal import Decimal

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe


class TimeframeBuilder:
    """
    Dynamically aggregates 1-minute (1M) candles into higher timeframes.
    Prevents database bloat and ensures mathematical consistency.
    """

    @staticmethod
    def _get_minutes_for_timeframe(tf: Timeframe) -> int:
        mapping = {
            Timeframe.M1: 1,
            Timeframe.M5: 5,
            Timeframe.M15: 15,
            Timeframe.H1: 60,
            Timeframe.H4: 240,
            Timeframe.D1: 1440,
        }
        return mapping.get(tf, 1)

    @staticmethod
    def aggregate(candles_1m: List[Candle], target_timeframe: Timeframe) -> List[Candle]:
        """
        Aggregates a list of chronologically sorted 1M candles into the target timeframe.
        """
        if not candles_1m:
            return []

        if target_timeframe == Timeframe.M1:
            return candles_1m

        target_minutes = TimeframeBuilder._get_minutes_for_timeframe(target_timeframe)
        aggregated = []
        
        current_bucket_start = None
        current_open = None
        current_high = None
        current_low = None
        current_close = None
        current_volume = Decimal("0")
        
        instrument = candles_1m[0].instrument
        source = candles_1m[0].source

        for candle in candles_1m:
            # We determine the "bucket" this candle belongs to.
            # Example: 10:01, 10:02, 10:03, 10:04, 10:00 belong to the 10:00 (5M) bucket.
            ts = candle.timestamp
            
            # This is a simplified bucketing based on minute truncation.
            # A full implementation should use MarketCalendar for session alignment.
            minute_of_day = ts.hour * 60 + ts.minute
            bucket_minute = (minute_of_day // target_minutes) * target_minutes
            bucket_hour = bucket_minute // 60
            bucket_min_rem = bucket_minute % 60
            
            bucket_start = ts.replace(hour=bucket_hour, minute=bucket_min_rem, second=0, microsecond=0)

            # If we enter a new bucket, save the previous one and reset
            if current_bucket_start is not None and bucket_start != current_bucket_start:
                aggregated.append(
                    Candle(
                        instrument=instrument,
                        timeframe=target_timeframe,
                        timestamp=current_bucket_start,
                        open=current_open,
                        high=current_high,
                        low=current_low,
                        close=current_close,
                        volume=current_volume,
                        source=source
                    )
                )
                
                # Reset for new bucket
                current_bucket_start = bucket_start
                current_open = candle.open
                current_high = candle.high
                current_low = candle.low
                current_close = candle.close
                current_volume = candle.volume
            else:
                if current_bucket_start is None:
                    current_bucket_start = bucket_start
                    current_open = candle.open
                    current_high = candle.high
                    current_low = candle.low
                else:
                    current_high = max(current_high, candle.high)
                    current_low = min(current_low, candle.low)
                    
                current_close = candle.close  # Always the latest close
                current_volume += candle.volume

        # Append the final bucket
        if current_bucket_start is not None:
            aggregated.append(
                Candle(
                    instrument=instrument,
                    timeframe=target_timeframe,
                    timestamp=current_bucket_start,
                    open=current_open,
                    high=current_high,
                    low=current_low,
                    close=current_close,
                    volume=current_volume,
                    source=source
                )
            )

        return aggregated
