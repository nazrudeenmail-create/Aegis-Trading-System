import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.validators.candle_validator import CandleValidator
from app.market.exceptions import InvalidCandleError

def create_valid_candle(timestamp: datetime = None, instrument: str = "EURUSD", timeframe: Timeframe = Timeframe.M1) -> Candle:
    if not timestamp:
        timestamp = datetime.now(timezone.utc)
    return Candle(
        instrument=instrument,
        timeframe=timeframe,
        timestamp=timestamp,
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("100"),
        source="test"
    )

def test_negative_prices_fail():
    candle = create_valid_candle().model_copy(update={"open": Decimal("-1")})
    with pytest.raises(InvalidCandleError, match="Negative price"):
        CandleValidator.validate_single(candle)

def test_negative_volume_fails():
    candle = create_valid_candle().model_copy(update={"volume": Decimal("-100")})
    with pytest.raises(InvalidCandleError, match="Volume cannot be negative"):
        CandleValidator.validate_single(candle)

def test_high_low_inversion_fails():
    candle = create_valid_candle().model_copy(update={"high": Decimal("90")}) # High lower than low (95)
    with pytest.raises(InvalidCandleError, match="High price must be >="):
        CandleValidator.validate_single(candle)
        
    candle2 = create_valid_candle().model_copy(update={"low": Decimal("110")}) # Low higher than high
    with pytest.raises(InvalidCandleError, match="Low price must be <="):
        CandleValidator.validate_single(candle2)

    candle3 = create_valid_candle().model_copy(update={"open": Decimal("100"), "close": Decimal("100"), "high": Decimal("105"), "low": Decimal("110")})
    with pytest.raises(InvalidCandleError, match="Low price must be <="):
        CandleValidator.validate_single(candle3)

def test_mixed_instruments_fails():
    c1 = create_valid_candle(instrument="EURUSD")
    c2 = create_valid_candle(instrument="GBPUSD")
    with pytest.raises(InvalidCandleError, match="Mixed instruments"):
        CandleValidator.validate_sequence([c1, c2])

def test_mixed_timeframes_fails():
    c1 = create_valid_candle(timeframe=Timeframe.M1)
    c2 = create_valid_candle(timeframe=Timeframe.H1)
    with pytest.raises(InvalidCandleError, match="Mixed timeframes"):
        CandleValidator.validate_sequence([c1, c2])

def test_out_of_order_sequence_fails():
    base = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    c1 = create_valid_candle(timestamp=base)
    c2 = create_valid_candle(timestamp=base - timedelta(minutes=1)) # Older candle after newer
    
    with pytest.raises(InvalidCandleError, match="out of chronological order"):
        CandleValidator.validate_sequence([c1, c2])

def test_duplicate_sequence_fails():
    base = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    c1 = create_valid_candle(timestamp=base)
    c2 = create_valid_candle(timestamp=base)
    
    with pytest.raises(InvalidCandleError, match="out of chronological order"):
        CandleValidator.validate_sequence([c1, c2])
