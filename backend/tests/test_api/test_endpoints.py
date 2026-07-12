import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.schemas import SystemStatusResponse, MarketSnapshotResponse, RankingResponse

client = TestClient(app)

# Dummy API Key for testing
HEADERS = {"X-API-Key": "dummy_key"}

# Need to mock the dependency for User authentication since we haven't seeded the DB
def override_get_current_user():
    from app.database.models.user import User
    from app.database.enums import UserRole
    return User(id=1, username="test_admin", api_key_hash="dummy", role=UserRole.ADMIN, is_active=True)

from app.api.auth import get_current_user
app.dependency_overrides[get_current_user] = override_get_current_user

def test_system_status_schema():
    response = client.get("/api/v1/system/status", headers=HEADERS)
    assert response.status_code == 200
    
    # Verify response matches the Pydantic schema
    data = response.json()
    status_obj = SystemStatusResponse(**data)
    
    assert status_obj.system == "ATS"
    assert status_obj.status == "healthy"

def test_market_snapshot_schema():
    response = client.get("/api/v1/market/current", headers=HEADERS)
    assert response.status_code == 200
    
    data = response.json()
    market_obj = MarketSnapshotResponse(**data)
    
    assert market_obj.symbol == "NVDA"
    assert market_obj.trend.direction == "BULLISH"

def test_ranking_result_schema():
    response = client.get("/api/v1/strategy/ranking", headers=HEADERS)
    assert response.status_code == 200
    
    data = response.json()
    ranking_obj = RankingResponse(**data)
    
    assert ranking_obj.winner == "EMA Trend Pullback"
    assert len(ranking_obj.ranking) > 0

def test_journal_latest_schema():
    response = client.get("/api/v1/journal/latest", headers=HEADERS)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "decision_id" in data[0]

def test_auth_unauthorized():
    # Clear overrides to test auth rejection
    app.dependency_overrides.clear()
    
    response = client.get("/api/v1/system/status") # Missing API key
    assert response.status_code == 401
    
    # Restore override for other tests if needed
    app.dependency_overrides[get_current_user] = override_get_current_user
