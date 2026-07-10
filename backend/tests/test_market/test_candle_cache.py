import pytest
from datetime import datetime, timezone
from decimal import Decimal

from app.market.cache.candle_cache import CandleCache
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe

def test_cache_tuple_keys():
    """
    Tier 2 Test: Ensure tuple keys perfectly isolate data.
    """
    cache = CandleCache()
    c1 = Candle(
        instrument="EURUSD", timeframe=Timeframe.M1, timestamp=datetime.now(timezone.utc),
        open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=Decimal("1"), source="test"
    )
    c2 = Candle(
        instrument="EURUSD", timeframe=Timeframe.H1, timestamp=datetime.now(timezone.utc),
        open=Decimal("2"), high=Decimal("2"), low=Decimal("2"), close=Decimal("2"), volume=Decimal("2"), source="test"
    )
    
    cache.append("EURUSD", Timeframe.M1, c1)
    cache.append("EURUSD", Timeframe.H1, c2)
    
    m1_list = cache.get("EURUSD", Timeframe.M1)
    h1_list = cache.get("EURUSD", Timeframe.H1)
    
    assert len(m1_list) == 1
    assert m1_list[0].open == Decimal("1")
    
    assert len(h1_list) == 1
    assert h1_list[0].open == Decimal("2")

def test_cache_eviction():
    """
    Ensure the cache respects the max_size boundary.
    """
    cache = CandleCache(max_size=5)
    base_time = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    
    # Append 10 items
    for i in range(10):
        c = Candle(
            instrument="EURUSD", timeframe=Timeframe.M1, timestamp=base_time,
            open=Decimal(str(i)), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=Decimal("1"), source="test"
        )
        cache.append("EURUSD", Timeframe.M1, c)
        
    result = cache.get("EURUSD", Timeframe.M1)
    assert len(result) == 5
    # Since we appended 0-9, the last 5 should be 5, 6, 7, 8, 9
    assert result[0].open == Decimal("5")
    assert result[-1].open == Decimal("9")
    
    # Test set() method eviction
    new_candles = []
    for i in range(10):
        new_candles.append(Candle(
            instrument="EURUSD", timeframe=Timeframe.M1, timestamp=base_time,
            open=Decimal(str(i)), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=Decimal("1"), source="test"
        ))
    cache.set("EURUSD", Timeframe.M1, new_candles)
    
    result2 = cache.get("EURUSD", Timeframe.M1)
    assert len(result2) == 5

def test_cache_get_returns_copy_not_reference():
    """
    Ensure retrieving from the cache and modifying the list doesn't corrupt internal cache.
    """
    cache = CandleCache()
    c = Candle(
        instrument="EURUSD", timeframe=Timeframe.M1, timestamp=datetime.now(timezone.utc),
        open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=Decimal("1"), source="test"
    )
    cache.append("EURUSD", Timeframe.M1, c)
    
    retrieved = cache.get("EURUSD", Timeframe.M1)
    assert len(retrieved) == 1
    
    # Mutate the retrieved list
    retrieved.pop()
    assert len(retrieved) == 0
    
    # Check internal cache
    internal = cache.get("EURUSD", Timeframe.M1)
    assert len(internal) == 1, "Cache was silently corrupted by external mutation!"
