from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter(prefix="/risk", tags=["risk"])

@router.get("/profile")
def get_risk_profile(current_user: User = Depends(get_current_user)):
    if not global_state.risk_engine:
        raise HTTPException(status_code=503, detail="Risk Engine not running")
        
    profile = global_state.risk_engine.profile
    return {
        "max_daily_loss": float(profile.max_daily_loss),
        "max_open_positions": profile.max_open_positions,
        "max_risk_per_trade": float(profile.max_risk_per_trade),
        "max_drawdown": float(profile.max_drawdown_limit),
        "min_margin_level": float(profile.min_margin_level)
    }
