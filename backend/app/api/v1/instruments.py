from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models.instrument import Instrument
from app.database.models.instrument_group import InstrumentGroup
from app.database.enums import InstrumentStatus, MarketType
from app.core.state import global_state

router = APIRouter(prefix="/instruments", tags=["instruments"])

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
            "paper_trading_enabled": i.paper_trading_enabled,
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

@router.post("/")
def create_instrument(instrument: InstrumentCreate, db: Session = Depends(get_db)):
    """Add a new instrument to the system."""
    existing = db.execute(select(Instrument).where(Instrument.symbol == instrument.symbol)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Instrument already exists")
        
    from app.database.enums import AssetClass
    asset_map = {
        "US_STOCK": AssetClass.STOCK,
        "CRYPTO": AssetClass.CRYPTO,
        "INDEX_CFD": AssetClass.INDEX,
        "FOREX": AssetClass.FOREX,
        "COMMODITY": AssetClass.COMMODITY
    }
    
    new_instrument = Instrument(
        symbol=instrument.symbol,
        name=instrument.name,
        market_type=MarketType[instrument.market_type],
        asset_class=asset_map.get(instrument.market_type, AssetClass.STOCK),
        exchange="CAPITAL",
        tick_size=0.01,
        contract_size=1.0,
        currency="USD",
        status=InstrumentStatus.WATCHLIST,
        trading_enabled=False,
        paper_trading_enabled=True,
        live_trading_enabled=False,
        allow_new_positions=False
    )
    db.add(new_instrument)
    db.commit()
    
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

@router.get("/groups")
def list_groups(db: Session = Depends(get_db)):
    """List all instrument groups."""
    result = db.execute(select(InstrumentGroup))
    groups = result.scalars().all()
        
    return [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description
        }
        for g in groups
    ]

@router.get("/market-sessions")
def get_market_sessions(db: Session = Depends(get_db)):
    """Returns current session states for all active/watchlist symbols."""
    # Only ACTIVE or WATCHLIST
    result = db.execute(select(Instrument).where(Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST])))
    instruments = result.scalars().all()
        
    session_manager = global_state.session_manager
    if not session_manager:
        # Fallback if manager not initialized
        return {i.symbol: "UNKNOWN" for i in instruments}
        
    return {
        i.symbol: session_manager.get_current_session_state(i.market_type).value
        for i in instruments
    }
