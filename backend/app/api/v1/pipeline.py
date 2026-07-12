from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.api.auth import get_current_user, User
from app.core.state import global_state
from pydantic import BaseModel

router = APIRouter()

class PipelineStatusResponse(BaseModel):
    symbol: str
    session: str
    data_status: str
    intelligence_status: str
    strategy_status: str
    ranking_score: float
    risk_status: str
    position_status: str

@router.get("/status", response_model=PipelineStatusResponse)
def get_pipeline_status(symbol: str, current_user: User = Depends(get_current_user)):
    """
    Returns the real-time status of the pipeline for a specific symbol.
    """
    session = "UNKNOWN"
    if global_state.session_manager:
        # We'd ideally need market_type here, default to UNKNOWN or derive from symbol
        session = "REGULAR"

    data_status = "No data"
    if global_state.market_service:
        data_status = "Loaded"

    intelligence_status = "-"
    strategy_status = "-"
    ranking_score = 0.0

    if global_state.ranking_engine:
        ranking = global_state.ranking_engine.get_latest_ranking(symbol)
        if ranking and ranking.rankings:
            strategy_status = ranking.selected_strategy if ranking.selected_strategy else "-"
            intelligence_status = "READY"
            for r in ranking.rankings:
                if r.strategy_name == strategy_status:
                    ranking_score = r.final_score
                    break

    risk_status = "-"
    position_status = "-"
    
    if global_state.broker_manager and global_state.broker_manager._active_broker:
        if hasattr(global_state.broker_manager._active_broker, 'positions'):
            for pos in global_state.broker_manager._active_broker.positions:
                if pos.symbol == symbol:
                    position_status = "OPEN"
                    break

    return PipelineStatusResponse(
        symbol=symbol,
        session=session,
        data_status=data_status,
        intelligence_status=intelligence_status,
        strategy_status=strategy_status,
        ranking_score=ranking_score,
        risk_status=risk_status,
        position_status=position_status
    )
