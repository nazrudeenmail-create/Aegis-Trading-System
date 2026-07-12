from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.api.schemas import SystemStatusResponse
from app.api.auth import get_current_user, User
from app.core.state import global_state

router = APIRouter()

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(current_user: User = Depends(get_current_user)):
    """
    Returns the overall health and operational status of the ATS.
    Requires authentication.
    """
    balance = 0.0
    open_positions = 0
    broker_name = "None"
    
    if global_state.paper_broker:
        broker_name = "PaperBroker"
        balance = float(await global_state.paper_broker.get_account_balance())
        open_positions = len(global_state.paper_broker.positions)
        
    return SystemStatusResponse(
        system="ATS",
        status="healthy",
        mode=global_state.mode,
        broker=broker_name,
        balance=balance,
        open_positions=open_positions,
        last_update=datetime.now(timezone.utc)
    )
