from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.instrument import Instrument
from app.database.models.instrument_group import InstrumentGroup
from app.database.enums import InstrumentStatus, MarketType, ExecutionMode
from app.core.state import global_state

router = APIRouter(prefix="/instruments")

@router.get("/")
def list_instruments(db: Session = Depends(get_db)):
    """List all instruments with their statuses and permissions."""
    result = db.execute(select(Instrument))
    instruments = result.scalars().all()
    return [
        {
            "id": i.id,
            "symbol": i.symbol,
            "name": i.name,
            "status": i.status.value,
            "market_type": i.market_type.value,
            "trading_enabled": i.trading_enabled,
            "execution_mode": i.execution_mode.value,
            "live_trading_enabled": i.live_trading_enabled,
            "allow_new_positions": i.allow_new_positions
        }
        for i in instruments
    ]

from pydantic import BaseModel
class InstrumentCreate(BaseModel):
    symbol: str
    name: str
    market_type: str

from fastapi import BackgroundTasks

def background_fetch_candles(instrument_id: int):
    # Setup a new DB session for the background task
    from app.database.connection import SessionLocal
    db = SessionLocal()
    try:
        fetch_historical_candles(instrument_id=instrument_id, db=db)
    finally:
        db.close()

@router.post("/")
def create_instrument(instrument: InstrumentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Add a new instrument to the system."""
    existing = db.execute(select(Instrument).where(Instrument.symbol == instrument.symbol)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Instrument already exists")
    from app.database.enums import AssetClass
    asset_map = {
        "US_STOCK": AssetClass.STOCK, "CRYPTO": AssetClass.CRYPTO,
        "INDEX_CFD": AssetClass.INDEX, "FOREX": AssetClass.FOREX,
        "COMMODITY": AssetClass.COMMODITY
    }
    new_instrument = Instrument(
        symbol=instrument.symbol, name=instrument.name,
        market_type=MarketType[instrument.market_type],
        asset_class=asset_map.get(instrument.market_type, AssetClass.STOCK),
        exchange="CAPITAL", tick_size=0.01, contract_size=1.0, currency="USD",
        status=InstrumentStatus.ACTIVE, trading_enabled=False,
        execution_mode=ExecutionMode.DEMO, live_trading_enabled=False, allow_new_positions=False
    )
    db.add(new_instrument)
    db.commit()
    db.refresh(new_instrument)
    
    # Trigger historical fetch
    background_tasks.add_task(background_fetch_candles, new_instrument.id)
    
    return {"status": "success", "symbol": instrument.symbol}

@router.patch("/{instrument_id}")
def update_instrument(instrument_id: int, updates: Dict[str, Any], db: Session = Depends(get_db)):
    """Update status or permissions of an instrument."""
    result = db.execute(select(Instrument).where(Instrument.id == instrument_id))
    instrument = result.scalar_one_or_none()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    for key, value in updates.items():
        if hasattr(instrument, key):
            setattr(instrument, key, value)
    db.commit()
    return {"status": "success", "instrument_id": instrument_id}

@router.post("/{instrument_id}/fetch-candles")
def fetch_historical_candles(instrument_id: int, db: Session = Depends(get_db)):
    """Download historical 1M candles from the broker and store in DB.
    
    Uses MarketDataService → BrokerFactory → CapitalComProvider.
    This endpoint does NOT construct provider/broker objects directly.
    """
    instrument = db.execute(select(Instrument).where(Instrument.id == instrument_id)).scalar_one_or_none()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    try:
        from app.market.domain.timeframe import Timeframe as DomainTimeframe
        from app.market.broker_factory import BrokerFactory
        from app.services.market_data_service import MarketDataService
        from app.core.config import get_settings
        settings = get_settings()
        
        # Get provider from BrokerFactory (cached singleton)
        provider = BrokerFactory.create_provider()
        service = MarketDataService(provider=provider)
        
        result = service.fetch_and_store_historical_candles(
            symbol=instrument.symbol,
            timeframe=DomainTimeframe.M1,
            limit=settings.INITIAL_HISTORY_CANDLES,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch candles: {str(e)}")

@router.get("/{instrument_id}/candles")
def get_candles(instrument_id: int, timeframe: str = "15M", count: int = 200, db: Session = Depends(get_db)):
    """Returns aggregated OHLCV candles for chart rendering."""
    instrument = db.execute(select(Instrument).where(Instrument.id == instrument_id)).scalar_one_or_none()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    try:
        from app.market.domain.timeframe import Timeframe as DomainTimeframe
        from app.database.repositories.candle_repository import CandleRepository
        from app.market.timeframe_builder import TimeframeBuilder
        tf_enum = DomainTimeframe[timeframe] if timeframe in DomainTimeframe.__members__ else DomainTimeframe.M15
        repo = CandleRepository(db)
        base_candles = repo.get_latest(instrument=instrument.symbol, limit=count * 10)
        if not base_candles:
            return {"symbol": instrument.symbol, "timeframe": timeframe, "candles": []}
        aggregated = TimeframeBuilder.aggregate(base_candles, tf_enum)
        return {
            "symbol": instrument.symbol, "timeframe": timeframe, "count": len(aggregated),
            "candles": [
                {"timestamp": c.timestamp.isoformat(), "open": float(c.open),
                 "high": float(c.high), "low": float(c.low),
                 "close": float(c.close), "volume": float(c.volume)}
                for c in aggregated[-count:]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candles: {str(e)}")

@router.get("/groups")
def list_groups(db: Session = Depends(get_db)):
    """List all instrument groups."""
    result = db.execute(select(InstrumentGroup))
    groups = result.scalars().all()
    return [{"id": g.id, "name": g.name, "description": g.description} for g in groups]

@router.get("/market-sessions")
def get_market_sessions(db: Session = Depends(get_db)):
    """Returns current session states for all active/watchlist symbols."""
    result = db.execute(select(Instrument).where(Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST])))
    instruments = result.scalars().all()
    session_manager = global_state.session_manager
    if not session_manager:
        return {i.symbol: "UNKNOWN" for i in instruments}
    return {i.symbol: session_manager.get_current_session_state(i.market_type).value for i in instruments}