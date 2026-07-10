import pytest
import responses
from decimal import Decimal
from datetime import datetime, timezone

from app.market.providers.capital_com_provider import CapitalComProvider
from app.market.domain.timeframe import Timeframe
from app.market.domain.candle import Candle
from app.market.exceptions import InvalidCandleError

@pytest.fixture
def provider():
    return CapitalComProvider(
        api_url="https://api-capital.backend-capital.com/api/v1",
        api_key="test_key",
        username="test_user",
        password="test_password"
    )

@responses.activate
def test_provider_returns_domain_candle_only(provider):
    """
    Tier 1 Critical Test: Ensure Capital.com JSON strictly transforms to Domain Candle
    and does not leak internal schema.
    """
    # Mock authentication
    responses.add(
        responses.POST, 
        "https://api-capital.backend-capital.com/api/v1/session",
        json={"accountType": "CFD"}, status=200,
        headers={"CST": "token_cst", "X-SECURITY-TOKEN": "token_sec"}
    )
    
    # Mock prices
    mock_json = {
        "prices": [
            {
                "snapshotTime": "2026-07-10T10:00:00",
                "openPrice": {"bid": 1.1000},
                "highPrice": {"bid": 1.1050},
                "lowPrice": {"bid": 1.0950},
                "closePrice": {"bid": 1.1020},
                "lastTradedVolume": 1500
            }
        ]
    }
    
    responses.add(
        responses.GET,
        "https://api-capital.backend-capital.com/api/v1/prices/EURUSD",
        json=mock_json, status=200
    )
    
    candles = provider.fetch_historical_candles("EURUSD", Timeframe.M1, 1)
    
    assert len(candles) == 1
    candle = candles[0]
    
    # Verify it's strictly a Domain Candle
    assert isinstance(candle, Candle)
    assert candle.open == Decimal("1.1000")
    
    # Verify NO JSON LEAKAGE
    assert not hasattr(candle, "openPrice"), "Capital.com schema leaked into Domain object!"
    assert not hasattr(candle, "lastTradedVolume"), "Capital.com schema leaked into Domain object!"

@responses.activate
def test_missing_bid_raises_error(provider):
    responses.add(
        responses.POST, 
        "https://api-capital.backend-capital.com/api/v1/session",
        json={}, status=200,
        headers={"CST": "token_cst", "X-SECURITY-TOKEN": "token_sec"}
    )
    
    mock_json = {
        "prices": [
            {
                "snapshotTime": "2026-07-10T10:00:00",
                "openPrice": {"ask": 1.1000}, # MISSING BID
                "highPrice": {"ask": 1.1050},
                "lowPrice": {"ask": 1.0950},
                "closePrice": {"ask": 1.1020},
                "lastTradedVolume": 1500
            }
        ]
    }
    
    responses.add(
        responses.GET,
        "https://api-capital.backend-capital.com/api/v1/prices/EURUSD",
        json=mock_json, status=200
    )
    
    with pytest.raises(InvalidCandleError, match="Missing bid price"):
        provider.fetch_historical_candles("EURUSD", Timeframe.M1, 1)

@responses.activate
def test_iso_utc_parsing(provider):
    responses.add(
        responses.POST, 
        "https://api-capital.backend-capital.com/api/v1/session",
        json={}, status=200,
        headers={"CST": "token_cst", "X-SECURITY-TOKEN": "token_sec"}
    )
    
    mock_json = {
        "prices": [
            {
                "snapshotTime": "2026-07-10T10:00:00Z", # With Z
                "openPrice": {"bid": 1.1000},
                "highPrice": {"bid": 1.1050},
                "lowPrice": {"bid": 1.0950},
                "closePrice": {"bid": 1.1020},
            }
        ]
    }
    
    responses.add(
        responses.GET,
        "https://api-capital.backend-capital.com/api/v1/prices/EURUSD",
        json=mock_json, status=200
    )
    
    candles = provider.fetch_historical_candles("EURUSD", Timeframe.M1, 1)
    
    assert candles[0].timestamp == datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
