import asyncio
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.analytics.events import EventBus

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to websocket: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time ATS events.
    """
    await manager.connect(websocket)
    import time
    welcome_msg = {
        "event": "system.log",
        "data": {
            "level": "INFO",
            "source": "System",
            "message": "Glass Box Console Connected. Awaiting system events...",
            "timestamp": int(time.time() * 1000)
        }
    }
    await websocket.send_json(welcome_msg)
    try:
        while True:
            # We don't expect messages from the client in this MVP, but we need to keep the connection open
            # and detect disconnects.
            data = await websocket.receive_text()
            # If client sends ping, we can echo pong
            if data.lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        manager.disconnect(websocket)

def init_websocket_broadcaster(event_bus: EventBus):
    """
    Subscribe the WebSocket manager to the EventBus.
    Called during application startup.
    """
    # Event types from Phase 10
    from app.analytics.events import DecisionEvent, ExecutionEvent, TradeClosedEvent, SystemLogEvent
    
    # We will wrap the sync publish into an async broadcast
    # Since EventBus handlers are sync right now, we need to schedule the coroutine
    def handle_decision(event: DecisionEvent):
        # We broadcast a ranking changed or risk rejected event
        if event.risk_assessment and not event.risk_assessment.is_approved:
            msg = {
                "event": "risk.rejected",
                "data": {
                    "symbol": event.symbol,
                    "strategy": event.ranking_result.selected_strategy,
                    "reason": event.risk_assessment.rejection_reason
                }
            }
        else:
            msg = {
                "event": "strategy.ranking.changed",
                "data": {
                    "symbol": event.symbol,
                    "winner": event.ranking_result.selected_strategy,
                    "score": float(event.ranking_result.rankings[0].final_score) if event.ranking_result.rankings else 0.0
                }
            }
        # Schedule the broadcast in the running asyncio loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast(msg))
        except RuntimeError:
            pass # Not running in an async loop (e.g., during some tests)
            
    def handle_execution(event: ExecutionEvent):
        msg = {
            "event": "trade.opened",
            "data": {
                "order_id": event.order_result.order_id,
                "status": event.order_result.status.value,
                "price": float(event.order_result.filled_price)
            }
        }
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast(msg))
        except RuntimeError:
            pass

    def handle_trade_closed(event: TradeClosedEvent):
        msg = {
            "event": "trade.closed",
            "data": {
                "trade_id": event.trade_record.trade_id,
                "pnl": float(event.trade_record.pnl),
                "strategy": event.trade_record.strategy_name
            }
        }
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast(msg))
        except RuntimeError:
            pass
    def handle_system_log(event: SystemLogEvent):
        import time
        msg = {
            "event": "system.log",
            "data": {
                "level": event.level,
                "source": event.source,
                "message": event.message,
                "timestamp": int(time.time() * 1000)
            }
        }
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast(msg))
        except RuntimeError:
            pass

    # Note: market.candle.closed and market.regime.changed are not yet explicitly modeled as EventBus events
    # We will add them here when Phase 3/4 gets integrated into the EventBus.
    
    event_bus.subscribe(DecisionEvent, handle_decision)
    event_bus.subscribe(ExecutionEvent, handle_execution)
    event_bus.subscribe(TradeClosedEvent, handle_trade_closed)
    event_bus.subscribe(SystemLogEvent, handle_system_log)
