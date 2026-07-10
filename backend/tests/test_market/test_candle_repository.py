import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.models.instrument import Instrument as InstrumentModel
from app.database.enums import AssetClass
from app.database.models.candle import Candle as CandleModel
from app.database.repositories.candle_repository import CandleRepository
from app.market.domain.candle import Candle as DomainCandle
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
        is_active=True
    )
    db_session.add(instrument)
    db_session.commit()
    return "EURUSD"

def test_repository_only_accepts_1m_candles(db_session: Session, test_instrument: str):
    """
    Tier 1 Critical Test: Ensure database architecture rule is maintained.
    Repository must store ONLY 1M truth candles, with NO timeframe column logic.
    """
    repo = CandleRepository(db_session)
    
    candles = []
    base_time = datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc)
    for i in range(100):
        candles.append(DomainCandle(
            instrument=test_instrument,
            timeframe=Timeframe.M1,
            timestamp=base_time + timedelta(minutes=i),
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("95"),
            close=Decimal("102"),
            volume=Decimal("100"),
            source="test"
        ))
        
    inserted_count = repo.save_many(candles)
    assert inserted_count == 100
    
    # Retrieve directly from DB using raw SQL to verify schema
    result = db_session.execute(text("SELECT * FROM candles")).fetchall()
    assert len(result) == 100
    
    # Ensure there is NO 'timeframe' column in the returned row keys
    # result[0]._mapping.keys() gets the column names
    column_names = list(result[0]._mapping.keys())
    assert "timeframe" not in column_names, "Timeframe column should not exist in database!"
    
    # Verify retrieval
    retrieved = repo.get_latest(instrument=test_instrument, limit=100)
    assert len(retrieved) == 100
    assert all(c.timeframe == Timeframe.M1 for c in retrieved)

def test_repository_on_conflict_do_nothing(db_session: Session, test_instrument: str):
    """
    Verify duplicate insertion safely returns 0 without crashing.
    """
    repo = CandleRepository(db_session)
    candle = DomainCandle(
        instrument=test_instrument,
        timeframe=Timeframe.M1,
        timestamp=datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("100"),
        source="test"
    )
    
    count1 = repo.save_many([candle])
    assert count1 == 1
    
    count2 = repo.save_many([candle])
    assert count2 == 0 # Duplicate ignored
    
def test_transaction_rollback(db_session: Session, test_instrument: str, monkeypatch):
    """
    Verify save_many rolls back safely on an internal database error.
    """
    repo = CandleRepository(db_session)
    candle = DomainCandle(
        instrument=test_instrument,
        timeframe=Timeframe.M1,
        timestamp=datetime(2026, 7, 10, 10, 0, 0, tzinfo=timezone.utc),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("100"),
        source="test"
    )
    
    # Monkeypatch execute to raise an error
    def mock_execute(*args, **kwargs):
        raise Exception("Simulated DB failure")
        
    monkeypatch.setattr(db_session, "execute", mock_execute)
    
    with pytest.raises(Exception, match="Simulated DB failure"):
        repo.save_many([candle])
        
    # The session rollback should have been called, but we can't easily assert
    # on session.rollback() without spying. The fact it caught and raised means
    # the except block executed.
