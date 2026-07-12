from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.api.schemas import SystemStatusResponse
from app.api.auth import get_current_user, User
from app.core.state import global_state

from app.api.dependencies import get_broker_manager
from app.execution.broker.manager import BrokerManager

router = APIRouter()

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    current_user: User = Depends(get_current_user),
    broker_manager: BrokerManager = Depends(get_broker_manager)
):
    """
    Returns the overall health and operational status of the ATS.
    Requires authentication.
    """
    balance = 0.0
    open_positions = 0
    broker_name = "None"
    
    if broker_manager._active_broker:
        broker_name = broker_manager.environment
        balance = float(await broker_manager.get_account_balance())
        if hasattr(broker_manager._active_broker, 'positions'):
            open_positions = len(broker_manager._active_broker.positions)
        
    engines = {
        "market": "Healthy" if global_state.market_service else "Offline",
        "strategy": "Healthy" if global_state.ranking_engine else "Offline",
        "risk": "Healthy" if global_state.risk_engine else "Offline",
        "execution": "Healthy" if global_state.execution_engine else "Offline"
    }

    return SystemStatusResponse(
        system="ATS",
        status="healthy",
        mode=global_state.mode,
        global_trading_mode=global_state.global_trading_mode,
        broker=broker_name,
        balance=balance,
        open_positions=open_positions,
        engines=engines,
        last_update=datetime.now(timezone.utc)
    )

from pydantic import BaseModel, field_validator
from fastapi import HTTPException

class SettingsUpdate(BaseModel):
    global_trading_mode: str

    @field_validator('global_trading_mode')
    @classmethod
    def validate_mode(cls, v):
        allowed = ["BROKER_DEMO", "BROKER_LIVE"]
        if v not in allowed:
            raise ValueError(f"Trading mode must be one of {allowed}")
        return v

@router.patch("/settings")
def update_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    global_state.global_trading_mode = settings_update.global_trading_mode
    # Note: A full implementation would also trigger BrokerManager to reconnect
    # if switching between live and demo. For now we just update the state.
    return {"message": "Settings updated", "global_trading_mode": global_state.global_trading_mode}
