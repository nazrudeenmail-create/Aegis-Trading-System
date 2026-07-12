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
    
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No recent market snapshot available for {symbol}")
        
    return MarketSnapshotResponse(
        symbol=snapshot.symbol,
        timeframe=snapshot.timeframe,
        price=snapshot.current_price,
        trend=TrendInfo(
            direction=snapshot.trend.direction.value,
            strength=snapshot.trend.strength.value
        ),
        regime=snapshot.regime.state.value,
        indicators=snapshot.indicators
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
