import pytest
from unittest.mock import Mock
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.services.candle_query_service import CandleQueryService
from app.market.domain.timeframe import Timeframe
from app.market.domain.candle import Candle

def test_query_calculates_correct_raw_limit():
    mock_repo = Mock()
    mock_repo.get_latest.return_value = []
    
    service = CandleQueryService(repository=mock_repo)
    service.get_latest("EURUSD", Timeframe.H1, 100)
    
    # H1 is 60 minutes. Requesting 100 limit. Buffer is 10.
    # Expected raw limit: (100 + 10) * 60 = 6600
    mock_repo.get_latest.assert_called_once_with(instrument="EURUSD", limit=6600)

def test_query_returns_exact_limit():
    mock_repo = Mock()
    base_time = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    
    # Simulate the DB returning 6600 raw candles
    raw_candles = []
    for i in range(6600):
        raw_candles.append(Candle(
            instrument="EURUSD", timeframe=Timeframe.M1, timestamp=base_time + timedelta(minutes=i),
            open=Decimal("1"), high=Decimal("1"), low=Decimal("1"), close=Decimal("1"), volume=Decimal("1"), source="test"
        ))
    
    mock_repo.get_latest.return_value = raw_candles
    
    service = CandleQueryService(repository=mock_repo)
    result = service.get_latest("EURUSD", Timeframe.H1, 100)
    
    # The builder will aggregate 6600 candles into exactly 110 H1 candles.
    # The service must slice the result to exactly 100.
    assert len(result) == 100
    assert result[0].timeframe == Timeframe.H1
