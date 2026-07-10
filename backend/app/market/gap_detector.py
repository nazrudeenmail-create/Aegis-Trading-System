from typing import List
from datetime import timedelta
from dataclasses import dataclass

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe

@dataclass
class Gap:
    start: str
    end: str
    missing_count: int

class GapDetector:
    """
    Detects missing candles in a sequence.
    """

    @staticmethod
    def _get_timeframe_delta(tf: Timeframe) -> timedelta:
        mapping = {
            Timeframe.M1: timedelta(minutes=1),
            Timeframe.M5: timedelta(minutes=5),
            Timeframe.M15: timedelta(minutes=15),
            Timeframe.H1: timedelta(hours=1),
            Timeframe.H4: timedelta(hours=4),
            Timeframe.D1: timedelta(days=1),
        }
        return mapping.get(tf, timedelta(minutes=1))

    @staticmethod
    def detect_gaps(candles: List[Candle]) -> List[Gap]:
        """
        Returns a list of Gap objects representing missing periods.
        Assumes candles are sorted chronologically.
        """
        gaps = []
        if not candles or len(candles) < 2:
            return gaps

        delta = GapDetector._get_timeframe_delta(candles[0].timeframe)
        delta_seconds = delta.total_seconds()

        for i in range(len(candles) - 1):
            current = candles[i]
            nxt = candles[i + 1]

            diff_seconds = (nxt.timestamp - current.timestamp).total_seconds()
            
            # In a production environment with a proper MarketCalendar,
            # weekend/holiday gaps would be ignored.
            if diff_seconds > delta_seconds:
                missing = int(diff_seconds // delta_seconds) - 1
                if missing > 0:
                    gaps.append(
                        Gap(
                            start=current.timestamp.isoformat(),
                            end=nxt.timestamp.isoformat(),
                            missing_count=missing
                        )
                    )

        return gaps
