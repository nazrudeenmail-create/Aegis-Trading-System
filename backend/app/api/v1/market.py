from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import MarketSnapshotResponse, TrendInfo
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter()

@router.get("/current", response_model=MarketSnapshotResponse)
def get_current_market(current_user: User = Depends(get_current_user)):
    """
    Returns the latest analyzed market snapshot from the Market Intelligence engine.
    """
    if not global_state.market_service:
        # Return a mock for Phase 11 UI dev if engine is not running
        return MarketSnapshotResponse(
            symbol="NVDA",
            timeframe="1H",
            price=182.50,
            trend=TrendInfo(direction="BULLISH", strength="STRONG"),
            regime="TRENDING",
            indicators={"ema20": 180.0, "ema50": 175.0, "adx": 32.0, "atr": 4.5}
        )
        
    # In future phases, fetch from actual MarketAnalysisService cache
    raise HTTPException(status_code=501, detail="Live market data not connected yet")
