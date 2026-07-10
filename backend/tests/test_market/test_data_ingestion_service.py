import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.services.data_ingestion_service import DataIngestionService
from app.market.domain.timeframe import Timeframe
from app.market.domain.candle import Candle
from app.market.exceptions import InvalidCandleError

def test_returns_inserted_count_not_fetched_count():
    """
    Tier 1 Critical Test: Ensure the service returns the number of actually 
    inserted rows, NOT the number fetched from the provider.
    """
    # Create 10 fake candles
    candles = []
    base_time = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    for i in range(10):
        candles.append(Candle(
            instrument="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=base_time, # Purposely making them the same timestamp isn't valid for sequence, but we can bypass validation or make them sequential
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("95"),
            close=Decimal("102"),
            volume=Decimal("100"),
            source="test"
        ))
        
    # We must make timestamps sequential so validate_sequence doesn't fail
    for i, c in enumerate(candles):
        candles[i] = c.model_copy(update={"timestamp": base_time + timedelta(minutes=i)})

    # Mock provider to return 10 candles
    mock_provider = Mock()
    mock_provider.fetch_historical_candles.return_value = candles
    
    # Mock repository to return 7 (e.g. 3 duplicates ignored)
    mock_repository = Mock()
    mock_repository.save_many.return_value = 7
    
    service = DataIngestionService(provider=mock_provider, repository=mock_repository)
    
    inserted_count = service.fetch_and_store_historical("EURUSD", Timeframe.M1, 10)
    
    # Service must return 7, not 10
    assert inserted_count == 7
    mock_repository.save_many.assert_called_once_with(candles)

def test_ingestion_aborts_on_validation_failure():
    """
    Ensure if validation fails, nothing is passed to the repository.
    """
    from datetime import timedelta
    
    base_time = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    # Create an invalid candle (negative price)
    bad_candle = Candle(
        instrument="EURUSD",
        timeframe=Timeframe.M1,
        timestamp=base_time,
        open=Decimal("-100"), # INVALID
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("100"),
        source="test"
    )
    
    mock_provider = Mock()
    mock_provider.fetch_historical_candles.return_value = [bad_candle]
    
    mock_repository = Mock()
    
    service = DataIngestionService(provider=mock_provider, repository=mock_repository)
    
    with pytest.raises(InvalidCandleError):
        service.fetch_and_store_historical("EURUSD", Timeframe.M1, 1)
        
    mock_repository.save_many.assert_not_called()
