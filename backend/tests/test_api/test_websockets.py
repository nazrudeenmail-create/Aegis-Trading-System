import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.analytics.events import event_bus, DecisionEvent
from app.strategy.models.ranking import RankingResult, StrategyScore
from app.market_analysis.enums import MarketRegime
from datetime import datetime, timezone

def test_websocket_connection_and_echo():
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"

@pytest.mark.asyncio
async def test_event_serialization():
    from app.api.v1.websocket import manager
    
    # Create a dummy websocket mock
    class DummyWebsocket:
        def __init__(self):
            self.messages = []
        async def send_json(self, msg):
            self.messages.append(msg)
            
    dummy = DummyWebsocket()
    manager.active_connections.append(dummy)
    
    await manager.broadcast({"event": "strategy.ranking.changed", "data": {"winner": "EMA"}})
    
    assert len(dummy.messages) == 1
    assert dummy.messages[0]["event"] == "strategy.ranking.changed"
    
    manager.active_connections.remove(dummy)
