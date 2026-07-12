from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import RankingResponse, StrategyScoreInfo
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter()

@router.get("/ranking", response_model=RankingResponse)
def get_strategy_ranking(current_user: User = Depends(get_current_user)):
    """
    Returns the latest output from the Strategy Ranking Engine (Phase 8).
    """
    if not global_state.ranking_engine:
        # Mock response for UI dev
        return RankingResponse(
            winner="EMA Trend Pullback",
            score=81.8,
            ranking=[
                StrategyScoreInfo(
                    strategy="EMA Trend Pullback",
                    total=81.8,
                    historical=54.6,
                    compatibility=100.0,
                    setup=100.0
                ),
                StrategyScoreInfo(
                    strategy="Donchian Breakout",
                    total=45.0
                )
            ]
        )
        
    raise HTTPException(status_code=501, detail="Ranking engine live feed not connected yet")
