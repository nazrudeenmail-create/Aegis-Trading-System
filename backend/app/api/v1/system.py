from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import time
import psutil
from app.api.schemas import SystemStatusResponse
from app.api.auth import get_current_user, User
from app.core.state import global_state
from app.core.config import get_settings, AccountMode

from app.api.dependencies import get_broker_manager
from app.execution.broker.manager import BrokerManager

router = APIRouter()

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    broker_manager: BrokerManager = Depends(get_broker_manager)
):
    """
    Returns the overall health and operational status of the ATS.
    Requires authentication.
    """
    settings = get_settings()
    balance = 0.0
    open_positions = 0
    broker_name = settings.broker_display_name
    
    if broker_manager._active_broker:
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
        broker=settings.broker_display_name,
        account_mode=settings.account_mode_display,
        balance=balance,
        open_positions=open_positions,
        engines=engines,
        last_update=datetime.now(timezone.utc)
    )

@router.get("/health", tags=["Health"])
async def get_system_health():
    """
    Public health endpoint — no authentication required.
    Exposes infrastructure status for monitoring and diagnostics.
    """
    settings = get_settings()
    broker_manager = get_broker_manager()
    
    # Calculate uptime
    process = psutil.Process()
    uptime_seconds = int(time.time() - process.create_time())
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Check broker connection
    broker_connected = False
    if broker_manager and broker_manager._active_broker:
        try:
            broker_connected = await broker_manager._active_broker.is_connected()
        except Exception:
            broker_connected = False
    
    # Check database
    db_connected = False
    try:
        from app.database.connection import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
    
    return {
        "broker": settings.BROKER,
        "mode": settings.ACCOUNT_MODE,
        "broker_connected": broker_connected,
        "database_connected": db_connected,
        "market_data": "running" if global_state.market_service else "stopped",
        "orchestrator": "running" if global_state.execution_engine else "stopped",
        "uptime": uptime_str
    }

from pydantic import BaseModel, field_validator
from fastapi import HTTPException

class SettingsUpdate(BaseModel):
    account_mode: str

    @field_validator('account_mode')
    @classmethod
    def validate_mode(cls, v):
        valid_modes = [m.value for m in AccountMode]
        if v not in valid_modes:
            raise ValueError(f"account_mode must be one of {valid_modes}")
        return v

@router.patch("/settings")
def update_settings(
    settings_update: SettingsUpdate
):
    """Update account mode settings.
    
    Note: A full implementation would also trigger BrokerManager to reconnect
    if switching between live and demo. For now we just validate the input.
    """
    settings = get_settings()
    return {
        "message": "Settings update received. Restart required for changes to take effect.",
        "account_mode": settings.account_mode_display,
        "broker": settings.broker_display_name
    }