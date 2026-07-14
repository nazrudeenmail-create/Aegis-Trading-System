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
            
    # 6. Engine Detailed Status
    engine_status = [
        {"name": "Broker", "status": broker_status.capitalize() if broker_status else "Disconnected", "color": "var(--success)" if broker_status == "CONNECTED" else "var(--danger)"},
        {"name": "Market Data", "status": "Healthy" if global_state.market_service else "Offline", "color": "var(--success)" if global_state.market_service else "var(--danger)"},
        {"name": "Analysis", "status": "Running" if global_state.market_service else "Offline", "color": "var(--accent-primary)" if global_state.market_service else "var(--danger)"},
        {"name": "Strategies", "status": "Running" if global_state.ranking_engine else "Offline", "color": "var(--accent-primary)" if global_state.ranking_engine else "var(--danger)"},
        {"name": "Risk", "status": "Ready", "color": "var(--success)"},
        {"name": "Orders", "status": "Idle", "color": "var(--text-tertiary)"},
        {"name": "Journal", "status": "Recording", "color": "var(--info)"},
    ]

    # 7. Market Cycle
    now_dt = datetime.now(timezone.utc)
    seconds = now_dt.second
    next_candle_sec = 60 - seconds
    
    pipeline_duration = "0 ms"
    pipeline_status = "Waiting"
    
    if global_state.telemetry:
        snapshot = global_state.telemetry.get_health_snapshot()
        strategy_latency = snapshot.get("latency", {}).get("Strategy", {})
        if strategy_latency:
            pipeline_duration = strategy_latency.get("last", "0 ms")
            
        strat_stage = snapshot.get("stages", {}).get("Strategy", {})
        pipeline_status = strat_stage.get("status", "Waiting")
        if pipeline_status == "Scanning":
            pipeline_status = "Processing..."
        elif pipeline_status in ["No Signal", "SUCCESS", "EVALUATED"]:
            pipeline_status = "Completed"
            
    market_cycle = {
        "next_candle": next_candle_sec,
        "last_candle": now_dt.replace(second=0, microsecond=0).strftime("%H:%M:00 UTC"),
        "status": pipeline_status,
        "duration": pipeline_duration
    }

    # 8. Events Pipeline
    events = []
    from app.analytics.events import event_bus, SystemLogEvent, DecisionEvent, ExecutionEvent, TradeClosedEvent
    for dt, evt in reversed(event_bus.history):
        event_time = dt.strftime("%H:%M:%S")
        if isinstance(evt, SystemLogEvent):
            evt_type = "info"
            if evt.level == "WARN": evt_type = "warning"
            elif evt.level == "ERROR": evt_type = "error"
            elif "started" in evt.message.lower() or "connected" in evt.message.lower() or "initialized" in evt.message.lower():
                evt_type = "success"
            events.append({
                "time": event_time,
                "type": evt_type,
                "text": evt.message,
                "sub": f"Source: {evt.source}"
            })
        elif isinstance(evt, DecisionEvent):
            events.append({
                "time": event_time,
                "type": "info",
                "text": f"Strategy {evt.ranking_result.selected_strategy} evaluated" if evt.ranking_result.selected_strategy else f"Market scanned, no setup",
                "sub": f"Instrument: {evt.symbol}"
            })
        elif isinstance(evt, ExecutionEvent):
            events.append({
                "time": event_time,
                "type": "success" if evt.order_result.status.value not in ["REJECTED", "CANCELLED"] else "error",
                "text": f"Order {evt.order_result.status.value.lower()}",
                "sub": f"Decision: {evt.decision_id}"
            })
        elif isinstance(evt, TradeClosedEvent):
            events.append({
                "time": event_time,
                "type": "success",
                "text": "Position closed",
                "sub": f"PnL: {evt.trade_record.pnl}"
            })

    # 9. Current Decision
    current_decision = None
    if global_state.journal and global_state.journal.decisions:
        # State 3: Decision Available
        latest_id = list(global_state.journal.decisions.keys())[-1]
        record = global_state.journal.decisions[latest_id]
        
        checks = []
        if record.historical_score is not None:
            checks.append({"name": "Historical Edge", "status": "PASS" if record.historical_score > 0 else "FAIL"})
        if record.compatibility_score is not None:
            checks.append({"name": "Market Compatibility", "status": "PASS" if record.compatibility_score > 0 else "FAIL"})
        if record.setup_score is not None:
            checks.append({"name": "Setup Quality", "status": "PASS" if record.setup_score > 0 else "FAIL"})
        if record.risk_approved is not None:
            checks.append({"name": "Risk Assessment", "status": "PASS" if record.risk_approved else "FAIL"})
            
        current_decision = {
            "state": "COMPLETED",
            "instrument": record.symbol,
            "strategy": record.selected_strategy or "NONE",
            "decision": "BUY" if record.selected_strategy and record.risk_approved else "WAIT",
            "readiness": int((record.final_score or 0) * 100),
            "reason": record.risk_reason if not record.risk_approved else ("Approved" if record.selected_strategy else "No strategy met criteria"),
            "checks": checks
        }
    else:
        # State 2: Scanning / Engine Working
        if global_state.ranking_engine:
            current_decision = {
                "state": "SCANNING",
                "instrument": "Scanning Markets...",
                "strategy": "Evaluation Engine Active",
                "decision": "EVALUATING",
                "readiness": 0,
                "reason": "Waiting for conditions",
                "checks": [
                    {"name": "Data Sync", "status": "PASS"},
                    {"name": "Indicators", "status": "PASS"},
                    {"name": "Strategy Scan", "status": "WAIT"}
                ]
            }
                
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
        "engine_status": engine_status,
        "market_cycle": market_cycle,
        "events": events,
        "current_decision": current_decision,
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
