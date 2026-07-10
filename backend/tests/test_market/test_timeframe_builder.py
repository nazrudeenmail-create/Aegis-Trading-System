import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.timeframe_builder import TimeframeBuilder

def test_1h_aggregation_accuracy():
    """
    Tier 1 Mathematical Test: 60 x 1M candles should correctly aggregate to 1 x 1H candle.
    """
    candles = []
    base_time = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    
    # Create 60 candles from 10:00 to 10:59
    # Open: first candle open
    # High: max of all
    # Low: min of all
    # Close: last candle close
    # Volume: sum of all
    
    for i in range(60):
        ts = base_time + timedelta(minutes=i)
        if i == 0:
            open_p, high_p, low_p, close_p, vol = 100, 105, 95, 102, 100
        elif i == 59:
            open_p, high_p, low_p, close_p, vol = 110, 120, 105, 120, 100
        elif i == 30: # inject the extreme max and min
            open_p, high_p, low_p, close_p, vol = 105, 130, 90, 110, 100
        else:
            open_p, high_p, low_p, close_p, vol = 105, 110, 100, 108, 100
            
        candles.append(Candle(
            instrument="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=ts,
            open=Decimal(str(open_p)),
            high=Decimal(str(high_p)),
            low=Decimal(str(low_p)),
            close=Decimal(str(close_p)),
            volume=Decimal(str(vol)),
            source="test"
        ))
        
    builder = TimeframeBuilder()
    aggregated = builder.aggregate(candles, Timeframe.H1)
    
    assert len(aggregated) == 1
    h1_candle = aggregated[0]
    
    assert h1_candle.timeframe == Timeframe.H1
    assert h1_candle.timestamp == base_time
    assert h1_candle.open == Decimal("100") # First candle open
    assert h1_candle.close == Decimal("120") # Last candle close
    assert h1_candle.high == Decimal("130") # Max high (at i=30)
    assert h1_candle.low == Decimal("90") # Min low (at i=30)
    assert h1_candle.volume == Decimal("6000") # 60 * 100

def test_d1_aggregation_accuracy():
    """
    Tier 1 Mathematical Test: Daily boundary test.
    """
    candles = []
    # 23:58, 23:59, 00:00, 00:01
    times = [
        datetime(2026, 7, 10, 23, 58, 0, tzinfo=timezone.utc),
        datetime(2026, 7, 10, 23, 59, 0, tzinfo=timezone.utc),
        datetime(2026, 7, 11, 0, 0, 0, tzinfo=timezone.utc),
        datetime(2026, 7, 11, 0, 1, 0, tzinfo=timezone.utc),
    ]
    for ts in times:
        candles.append(Candle(
            instrument="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=ts,
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("95"),
            close=Decimal("100"),
            volume=Decimal("100"),
            source="test"
        ))
        
    builder = TimeframeBuilder()
    aggregated = builder.aggregate(candles, Timeframe.D1)
    
    # Should result in 2 daily candles
    assert len(aggregated) == 2
    assert aggregated[0].timestamp == datetime(2026, 7, 10, 0, 0, tzinfo=timezone.utc)
    assert aggregated[0].volume == Decimal("200")
    assert aggregated[1].timestamp == datetime(2026, 7, 11, 0, 0, tzinfo=timezone.utc)
    assert aggregated[1].volume == Decimal("200")

def test_m1_passthrough():
    """
    Ensure M1 aggregation just passes through the original list.
    """
    candles = [
        Candle(
            instrument="EURUSD", timeframe=Timeframe.M1, 
            timestamp=datetime.now(timezone.utc), 
            open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=Decimal("1"), source="test"
        )
    ]
    builder = TimeframeBuilder()
    aggregated = builder.aggregate(candles, Timeframe.M1)
    
    assert len(aggregated) == 1
    assert aggregated[0] is candles[0]
