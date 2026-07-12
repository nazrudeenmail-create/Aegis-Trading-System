from fastapi import APIRouter, Depends
from datetime import datetime
from app.api.dependencies import get_broker_manager
from app.execution.broker.manager import BrokerManager
from app.execution.broker.models import ConnectionState

router = APIRouter(prefix="/broker", tags=["broker"])

@router.get("/connections")
async def get_broker_connections(broker_manager: BrokerManager = Depends(get_broker_manager)):
    """
    Returns detailed stats for the Broker Connections dashboard page.
    """
    
    # Paper Broker (always available locally)
    paper_broker = {
        "id": "paper",
        "name": "Internal Paper Broker",
        "type": "SIMULATION",
        "status": "CONNECTED",
        "description": "Runs locally, executing simulated orders against historical or live data feed."
    }
    
    # Active Broker Manager (e.g. Capital.com)
    active_broker = {
        "id": "capital",
        "name": "Capital.com",
        "environment": broker_manager.environment,
        "status": broker_manager.state.value,
        "latency_ms": broker_manager.latency_ms,
        "reconnects_today": broker_manager.reconnects_today,
        "api_health": "Healthy" if broker_manager.state == ConnectionState.CONNECTED else "Unknown",
        "last_heartbeat": None, # Should come from broker_manager auth but we'll mock for now
    }
    
    # Try to grab detailed auth state if available
    if broker_manager._active_broker and hasattr(broker_manager._active_broker, 'auth'):
        auth = broker_manager._active_broker.auth
        if hasattr(auth, 'last_heartbeat') and auth.last_heartbeat:
            active_broker["last_heartbeat"] = auth.last_heartbeat.isoformat()
            
    # Account Details Mock
    account_details = {
        "account_id": "83749210",
        "currency": "USD",
        "equity": 100000.0,
        "available_margin": 100000.0,
        "used_margin": 0.0
    }
    
    if broker_manager.state == ConnectionState.CONNECTED:
        try:
            account_details["equity"] = float(await broker_manager.get_account_balance())
            account_details["available_margin"] = account_details["equity"]
        except Exception:
            pass

    return {
        "connections": [paper_broker, active_broker],
        "active_account": account_details if broker_manager.state == ConnectionState.CONNECTED else None
    }
