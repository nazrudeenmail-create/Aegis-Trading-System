from typing import List

from app.market.domain.candle import Candle
from app.market.exceptions import InvalidCandleError


class CandleValidator:
    """
    Validates the mathematical correctness and sequence of market data candles.
    """

    @staticmethod
    def validate_single(candle: Candle) -> None:
        """
        Validates the OHLC integrity of a single candle.
        Raises InvalidCandleError if constraints are violated.
        """
        if candle.open < 0 or candle.high < 0 or candle.low < 0 or candle.close < 0:
            raise InvalidCandleError(f"Negative price found in candle: {candle}")

        if candle.high < candle.open or candle.high < candle.close:
            raise InvalidCandleError(f"High price must be >= Open and Close: {candle}")

        if candle.low > candle.open or candle.low > candle.close:
            raise InvalidCandleError(f"Low price must be <= Open and Close: {candle}")

        if candle.low > candle.high:
            raise InvalidCandleError(f"Low price cannot be > High price: {candle}")

        if candle.volume < 0:
            raise InvalidCandleError(f"Volume cannot be negative: {candle}")

    @staticmethod
    def validate_sequence(candles: List[Candle]) -> None:
        """
        Validates a sequence of candles for chronological order.
        Assumes the expected order is oldest first (ascending).
        """
        if not candles:
            return

        for i in range(len(candles) - 1):
            current = candles[i]
            nxt = candles[i + 1]

            if current.instrument != nxt.instrument:
                raise InvalidCandleError(
                    f"Mixed instruments in sequence: {current.instrument} and {nxt.instrument}"
                )

            if current.timeframe != nxt.timeframe:
                raise InvalidCandleError(
                    f"Mixed timeframes in sequence: {current.timeframe} and {nxt.timeframe}"
                )

            if current.timestamp >= nxt.timestamp:
                raise InvalidCandleError(
                    f"Timestamps out of chronological order or duplicated: {current.timestamp} followed by {nxt.timestamp}"
                )

            CandleValidator.validate_single(current)
            
        # Validate the last candle
        CandleValidator.validate_single(candles[-1])
