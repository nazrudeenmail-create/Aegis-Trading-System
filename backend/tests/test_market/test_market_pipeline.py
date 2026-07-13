import pytest
import responses
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.models.instrument import Instrument as InstrumentModel
from app.database.enums import AssetClass
from app.market.providers.capital_com_provider import CapitalComProvider
from app.database.repositories.candle_repository import CandleRepository
from app.services.data_ingestion_service import DataIngestionService
from app.services.candle_query_service import CandleQueryService
from app.market.domain.timeframe import Timeframe

@pytest.fixture
def test_instrument(db_session: Session) -> str:
    """Fixture to ensure the EURUSD instrument exists in the DB."""
    instrument = InstrumentModel(
        symbol="EURUSD",
        name="Euro vs US Dollar",
        asset_class=AssetClass.FOREX,
        exchange="CAPITAL_COM",
        tick_size=Decimal("0.0001"),
        contract_size=Decimal("1.0"),
        currency="USD",
    )
    db_session.add(instrument)
    db_session.commit()
    return "EURUSD"

@responses.activate
def test_end_to_end_market_data_pipeline(db_session: Session, test_instrument: str):
    """
    Tier 1 Critical Test: Complete end-to-end integration test.
    Mock Provider -> Ingestion Service -> PostgreSQL -> Query Service -> 1H Candles
    """
    
    # 1. Setup Mock Provider
    provider = CapitalComProvider(
        api_url="https://api-capital.backend-capital.com/api/v1",
        api_key="test_key",
        username="test_user",
        password="test_password"
    )
    
    responses.add(
        responses.POST, 
        "https://api-capital.backend-capital.com/api/v1/session",
        json={}, status=200,
        headers={"CST": "token_cst", "X-SECURITY-TOKEN": "token_sec"}
    )
    
    # Generate 6000 fake 1M responses (100 hours of data)
    prices = []
    base_time = datetime(2026, 7, 10, 0, 0, 0, tzinfo=timezone.utc)
    for i in range(6000):
        ts = base_time + timedelta(minutes=i)
        prices.append({
            "snapshotTime": ts.replace(tzinfo=None).isoformat() + "Z",
            "openPrice": {"bid": 1.1000},
            "highPrice": {"bid": 1.1050},
            "lowPrice": {"bid": 1.0950},
            "closePrice": {"bid": 1.1020},
            "lastTradedVolume": 100
        })
        
    responses.add(
        responses.GET,
        "https://api-capital.backend-capital.com/api/v1/prices/EURUSD",
        json={"prices": prices}, status=200
    )
    
    # 2. Setup Architecture Layers
    repository = CandleRepository(db_session)
    ingestion_service = DataIngestionService(provider, repository)
    query_service = CandleQueryService(repository)
    
    # 3. Ingest Data (Simulate backtest data loading)
    inserted_count = ingestion_service.fetch_and_store_historical("EURUSD", Timeframe.M1, 6000)
    assert inserted_count == 6000
    
    # 4. Verify Database Integrity (Strict 1M storage for this instrument)
    result = db_session.execute(
        text("SELECT COUNT(*) FROM candles WHERE instrument_id = (SELECT id FROM instruments WHERE symbol = :symbol)"),
        {"symbol": test_instrument}
    ).scalar()
    assert result == 6000
    
    # 5. Query Aggregated Data (Strategy asks for 100 1H candles)
    h1_candles = query_service.get_latest("EURUSD", Timeframe.H1, 100)
    
    # 6. Verify Final Outcome
    assert len(h1_candles) == 100
    
    # Spot-check the first and last 1H candle for mathematical accuracy
    first_h1 = h1_candles[0]
    last_h1 = h1_candles[-1]
    
    assert first_h1.timeframe == Timeframe.H1
    assert first_h1.volume == Decimal("6000") # 60 * 100
    assert first_h1.open == Decimal("1.1000")
    assert first_h1.close == Decimal("1.1020")
    
    assert last_h1.timeframe == Timeframe.H1
    assert last_h1.volume == Decimal("6000")
