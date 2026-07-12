from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import psutil

from app.database.connection import get_db
from app.database.models.instrument import Instrument
from app.database.enums import InstrumentStatus
from app.core.state import global_state
from app.api.dependencies import get_broker_manager
from app.execution.broker.manager import BrokerManager

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    broker_manager: BrokerManager = Depends(get_broker_manager)
):
    """An aggregate endpoint for initial fast dashboard load."""
    
    # 1. System Status
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    
    import time
    process = psutil.Process()
    uptime_seconds = time.time() - process.create_time()
    uptime_hours = round(uptime_seconds / 3600.0, 2)
    
    system_status = {
        "backend": "RUNNING",
        "database": "CONNECTED",
        "cpu_percent": cpu_usage,
        "memory_mb": int(memory_info.used / (1024 * 1024)),
        "uptime_hours": uptime_hours
    }
    
    # 2. Broker Status & Trading Mode
    trading_mode = global_state.global_trading_mode
    broker_status = broker_manager.state.value if broker_manager else "DISCONNECTED"
    
    # 3. Account Balance & Open Positions
    import asyncio
    try:
        account_balance = float(asyncio.run(broker_manager.get_account_balance()))
    except RuntimeError: # if loop is running
        account_balance = 0.0
        
    open_positions_count = 0
    unrealized_pnl = 0.0
    daily_pnl = 0.0
    
    if hasattr(broker_manager._active_broker, 'positions'):
        positions = broker_manager._active_broker.positions
        open_positions_count = len(positions)
        if isinstance(positions, dict):
            for pos in positions.values():
                unrealized_pnl += float(getattr(pos, 'unrealized_pnl', 0.0))
        elif isinstance(positions, list):
            for pos in positions:
                unrealized_pnl += float(getattr(pos, 'unrealized_pnl', 0.0))
            
    available_margin = account_balance # Simplified for now
    
    # 4. Active Instruments & Market Sessions
    result = db.execute(select(Instrument).where(Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST])))
    instruments = result.scalars().all()
        
    market_sessions = {}
    active_count = 0
    
    if global_state.session_manager:
        for i in instruments:
            market_sessions[i.symbol] = global_state.session_manager.get_current_session_state(i.market_type).value
            if i.status == InstrumentStatus.ACTIVE:
                active_count += 1
                
    return {
        "system_status": system_status,
        "trading_mode": trading_mode,
        "broker_status": broker_status,
        "account_balance": account_balance,
        "available_margin": available_margin,
        "unrealized_pnl": unrealized_pnl,
        "daily_pnl": daily_pnl,
        "open_positions": open_positions_count,
        "active_instruments_count": active_count,
        "market_sessions": market_sessions,
        "last_market_update": "N/A"
    }
