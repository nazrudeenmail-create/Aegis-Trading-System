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
        "account_balance": float(profile.account_balance),
        "risk_per_trade_percent": float(profile.risk_per_trade_percent),
        "max_open_risk_percent": float(profile.max_open_risk_percent),
        "max_daily_drawdown_percent": float(profile.max_daily_drawdown_percent),
        "allow_high_risk_mode": profile.allow_high_risk_mode
    }
