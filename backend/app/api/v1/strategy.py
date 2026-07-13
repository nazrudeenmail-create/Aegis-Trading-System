from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import RankingResponse, StrategyScoreInfo
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter()

@router.get("/ranking", response_model=RankingResponse)
def get_strategy_ranking(symbol: str = "BTCUSD", current_user: User = Depends(get_current_user)):
    """
    Returns the latest output from the Strategy Ranking Engine (Phase 8).
    """
    if not global_state.ranking_engine:
        raise HTTPException(status_code=503, detail="Ranking engine is not running")
        
    ranking = global_state.ranking_engine.get_latest_ranking(symbol)
    
    if not ranking or not ranking.rankings:
        raise HTTPException(status_code=404, detail=f"No recent ranking available for {symbol}")
        
    winner_name = ranking.selected_strategy
    winner_score = 0.0
    if winner_name:
        for r in ranking.rankings:
            if r.strategy_name == winner_name:
                winner_score = r.final_score
                break
        
    return RankingResponse(
        winner=winner_name if winner_name else "None",
        score=winner_score,
        ranking=[
            StrategyScoreInfo(
                strategy=candidate.strategy_name,
                total=candidate.final_score,
                historical=candidate.historical_score,
                compatibility=candidate.market_score,
                setup=candidate.setup_score
            )
            for candidate in ranking.rankings
        ]
    )

from pydantic import BaseModel
from typing import Dict, Any

class StrategyProfileUpdate(BaseModel):
    config: Dict[str, Any]

@router.get("/profiles")
def get_strategy_profiles():
    """Returns profiles of all registered strategies."""
    if not global_state.ranking_engine:
        raise HTTPException(status_code=503, detail="Ranking engine is not running")
    
    profiles = {}
    for strategy in global_state.ranking_engine.strategies:
        if hasattr(strategy, 'get_profile'):
            profile = strategy.get_profile()
            if hasattr(profile, 'model_dump'):
                dump = profile.model_dump()
            elif hasattr(profile, 'dict'):
                dump = profile.dict()
            else:
                dump = profile.__dict__
            # Convert values to strings if they are lists (like regimes) for simple frontend editing
            # Or just send the dict. Actually, the frontend expects the dict.
            profiles[strategy.name] = dump
        else:
            profiles[strategy.name] = {}
    return profiles

@router.patch("/{name}/profile")
def update_strategy_profile(name: str, update: StrategyProfileUpdate, current_user: User = Depends(get_current_user)):
    """Updates the profile configuration for a specific strategy."""
    if not global_state.ranking_engine:
        raise HTTPException(status_code=503, detail="Ranking engine is not running")
        
    for strategy in global_state.ranking_engine.strategies:
        if strategy.name == name:
            if not hasattr(strategy, 'profile'):
                raise HTTPException(status_code=400, detail="Strategy does not have a configurable profile")
            
            for k, v in update.config.items():
                if hasattr(strategy.profile, k):
                    setattr(strategy.profile, k, v)
            
            return {"status": "success", "strategy": name, "updated_profile": strategy.profile.__dict__}
            
    raise HTTPException(status_code=404, detail="Strategy not found")
