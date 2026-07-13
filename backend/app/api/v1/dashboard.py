from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
import psutil

from app.database.connection import get_db
from app.database.models.instrument import Instrument
from app.database.enums import InstrumentStatus
from app.core.state import global_state
from app.api.dependencies import get_broker_manager
from app.execution.broker.manager import BrokerManager

router = APIRouter(prefix="/dashboard")

@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    broker_manager: BrokerManager = Depends(get_broker_manager)
):
    """Aggregate endpoint for initial fast dashboard load. Returns structured portfolio/market/engine data."""
    
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
    from app.core.config import get_settings
    settings = get_settings()
    trading_mode = settings.account_mode_display
    broker_status = broker_manager.state.value if broker_manager else "DISCONNECTED"
    
    # 3. Account Balance & Open Positions
    try:
        account_balance = float(await broker_manager.get_account_balance())
    except Exception:
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
            
    # 4. Active Instruments & Market Session Counts
    result = db.execute(select(Instrument).where(Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST])))
    instruments = result.scalars().all()
        
    active_count = 0
    markets_open = 0
    markets_closed = 0
    
    for i in instruments:
        if i.status == InstrumentStatus.ACTIVE:
            active_count += 1
        if global_state.session_manager:
            try:
                session_val = global_state.session_manager.get_current_session_state(i.market_type).value
                if session_val in ("REGULAR", "EXTENDED"):
                    markets_open += 1
                else:
                    markets_closed += 1
            except Exception:
                markets_closed += 1

    # 5. Engine status
    strategies_running = 0
    if global_state.ranking_engine:
        try:
            strategies_running = len(global_state.ranking_engine.strategies)
        except Exception:
            pass
                
    return {
        "system_status": system_status,
        "trading_mode": trading_mode,
        "broker_status": broker_status,
        "account": {
            "balance": account_balance,
            "equity": account_balance,
            "available_margin": account_balance,
            "unrealized_pnl": unrealized_pnl,
            "daily_pnl": daily_pnl,
        },
        "portfolio": {
            "active_instruments": active_count,
            "open_positions": open_positions_count,
            "total_risk_percent": 0.0,
        },
        "market": {
            "markets_open": markets_open,
            "markets_closed": markets_closed,
        },
        "engine": {
            "strategies_running": strategies_running,
            "signals_today": 0,
        },
        "last_market_update": datetime.now(timezone.utc).isoformat()
    }


@router.get("/instruments")
def get_dashboard_instruments(db: Session = Depends(get_db)):
    """
    Returns all active/watchlist instruments with live analysis data as an array.

    Powers the Market Watch section and Strategy Scanner.
    Frontend simply loops: instruments.map(item => <InstrumentCard data={item}/>)
    Adding a new instrument via INSERT INTO instruments automatically appears here —
    zero frontend changes required.
    """
    result = db.execute(
        select(Instrument).where(
            Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST])
        )
    )
    instruments = result.scalars().all()
    
    items = []
    for i in instruments:
        # Market session state
        session_state = "UNKNOWN"
        if global_state.session_manager:
            try:
                session_state = global_state.session_manager.get_current_session_state(i.market_type).value
            except Exception:
                pass
        
        # Latest analysis snapshot from market service
        price = None
        trend = "NEUTRAL"
        regime = "UNKNOWN"
        adx = None
        signal = "NONE"
        
        if global_state.market_service:
            try:
                snapshot = global_state.market_service.get_latest_snapshot(i.symbol)
                if snapshot and snapshot.candles:
                    price = round(float(snapshot.candles[-1].close), 4)
                if snapshot and snapshot.trend:
                    trend = snapshot.trend.direction.value
                if snapshot and snapshot.regime and snapshot.regime.regime:
                    regime = snapshot.regime.regime.value
                if snapshot and snapshot.adx and snapshot.adx.adx:
                    adx = round(float(snapshot.adx.adx), 1)
            except Exception:
                pass
        
        # Strategy ranking signal
        top_strategy = None
        strategy_score = None
        if global_state.ranking_engine:
            try:
                ranking = global_state.ranking_engine.get_latest_ranking(i.symbol)
                if ranking and ranking.rankings:
                    best = ranking.rankings[0]
                    top_strategy = best.strategy_name
                    strategy_score = round(float(best.final_score), 1)
                    if ranking.selected_strategy:
                        signal = "SETUP_FOUND"
            except Exception:
                pass
        
        items.append({
            "id": i.id,
            "symbol": i.symbol,
            "name": i.name,
            "asset_class": i.asset_class.value,
            "market_type": i.market_type.value,
            "status": i.status.value,
            "session": session_state,
            "price": price,
            "trend": trend,
            "regime": regime,
            "adx": adx,
            "signal": signal,
            "top_strategy": top_strategy,
            "strategy_score": strategy_score,
        })
    
    return {"instruments": items}
