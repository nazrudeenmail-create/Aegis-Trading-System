from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import MarketSnapshotResponse, TrendInfo
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter()

@router.get("/current", response_model=MarketSnapshotResponse)
def get_current_market(symbol: str = "BTCUSD"):
    """
    Returns the latest analyzed market snapshot from the Market Intelligence engine.
    """
    if not global_state.market_service:
        raise HTTPException(status_code=503, detail="Market Service is not running")
        
    snapshot = global_state.market_service.get_latest_snapshot(symbol)
    
    if not snapshot or not snapshot.candles:
        raise HTTPException(status_code=404, detail=f"No recent market snapshot available for {symbol}")
        
    latest_candle = snapshot.candles[-1]
    
    direction = snapshot.trend.direction.value if snapshot.trend else "NEUTRAL"
    strength = snapshot.trend.strength.value if snapshot.trend else "WEAK"
    regime = snapshot.regime.regime.value if snapshot.regime and snapshot.regime.regime else "UNKNOWN"
    
    indicators = {}
    if snapshot.ema:
        indicators["ema"] = snapshot.ema.model_dump() if hasattr(snapshot.ema, 'model_dump') else snapshot.ema.dict()
    if snapshot.atr:
        indicators["atr"] = snapshot.atr.model_dump() if hasattr(snapshot.atr, 'model_dump') else snapshot.atr.dict()
    if snapshot.adx:
        indicators["adx"] = snapshot.adx.model_dump() if hasattr(snapshot.adx, 'model_dump') else snapshot.adx.dict()
    if snapshot.volume:
        indicators["volume"] = snapshot.volume.model_dump() if hasattr(snapshot.volume, 'model_dump') else snapshot.volume.dict()
    if snapshot.candle:
        indicators["candle"] = snapshot.candle.model_dump() if hasattr(snapshot.candle, 'model_dump') else snapshot.candle.dict()
    if snapshot.swing:
        indicators["swing"] = snapshot.swing.model_dump() if hasattr(snapshot.swing, 'model_dump') else snapshot.swing.dict()
    if snapshot.donchian:
        indicators["donchian"] = snapshot.donchian.model_dump() if hasattr(snapshot.donchian, 'model_dump') else snapshot.donchian.dict()
    if snapshot.pullback:
        indicators["pullback"] = snapshot.pullback.model_dump() if hasattr(snapshot.pullback, 'model_dump') else snapshot.pullback.dict()
    if snapshot.momentum:
        indicators["momentum"] = snapshot.momentum.model_dump() if hasattr(snapshot.momentum, 'model_dump') else snapshot.momentum.dict()
    if snapshot.volatility:
        indicators["volatility"] = snapshot.volatility.model_dump() if hasattr(snapshot.volatility, 'model_dump') else snapshot.volatility.dict()
        
    return MarketSnapshotResponse(
        symbol=latest_candle.instrument,
        timeframe=latest_candle.timeframe.value,
        price=float(latest_candle.close),
        trend=TrendInfo(
            direction=direction,
            strength=strength
        ),
        regime=regime,
        indicators=indicators
    )

@router.get("/broker/search")
async def search_broker_instruments(
    query: str
):
    """
    Search for available instruments on the active broker.
    """
    # Search for instruments via the active broker
    if global_state.broker_manager:
        results = await global_state.broker_manager.search_instruments(query)
        if results:
            return results
            
    # Fallback if no broker manager or empty
    return []

from app.database.connection import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.models.instrument import Instrument

@router.get("/candles")
def get_market_candles(
    symbol: str, 
    timeframe: str = "1h", 
    limit: int = 200, 
    db: Session = Depends(get_db)
):
    """Returns aggregated OHLCV candles for chart rendering."""
    instrument = db.execute(select(Instrument).where(Instrument.symbol == symbol)).scalar_one_or_none()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
        
    try:
        from app.market.domain.timeframe import Timeframe as DomainTimeframe
        from app.database.repositories.candle_repository import CandleRepository
        from app.market.timeframe_builder import TimeframeBuilder
        
        # Map frontend '1h' etc to DomainTimeframe.H1
        tf_map = {
            "1m": DomainTimeframe.M1, "5m": DomainTimeframe.M5, "15m": DomainTimeframe.M15,
            "1h": DomainTimeframe.H1, "4h": DomainTimeframe.H4, "1d": DomainTimeframe.D1
        }
        tf_enum = tf_map.get(timeframe.lower(), DomainTimeframe.H1)
        
        tf_minutes_map = {
            DomainTimeframe.M1: 1, DomainTimeframe.M5: 5, DomainTimeframe.M15: 15,
            DomainTimeframe.H1: 60, DomainTimeframe.H4: 240, DomainTimeframe.D1: 1440
        }
        minutes = tf_minutes_map.get(tf_enum, 60)
        
        repo = CandleRepository(db)
        base_candles = repo.get_latest(instrument=instrument.symbol, limit=limit * minutes)
        if not base_candles:
            return []
            
        aggregated = TimeframeBuilder.aggregate(base_candles, tf_enum)
        
        # The lightweight-charts library expects specific keys: time, open, high, low, close.
        # We need to map our domain candles to this format.
        formatted = [
            {
                "time": int(c.timestamp.timestamp()), 
                "open": float(c.open),
                "high": float(c.high), 
                "low": float(c.low),
                "close": float(c.close), 
                "volume": float(c.volume)
            }
            for c in aggregated[-limit:]
        ]
        return formatted
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get candles: {str(e)}")
