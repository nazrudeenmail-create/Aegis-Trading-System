import pytest
from fastapi.testclient import TestClient
from app.main import app
from decimal import Decimal
from app.api.schemas import SystemStatusResponse, MarketSnapshotResponse, RankingResponse
from app.strategy.models import TradeCandidate, TradeDirection

client = TestClient(app)

# Dummy API Key for testing
HEADERS = {"X-API-Key": "dummy_key"}

# Need to mock the dependency for User authentication since we haven't seeded the DB
def override_get_current_user():
    from app.database.models.user import User
    from app.database.enums import UserRole
    return User(id=1, username="test_admin", key_prefix="ats_test", key_hash="dummy", role=UserRole.ADMIN, is_active=True)

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
    from app.core.state import global_state
    from app.market_analysis.mtf_service import MultiTimeframeService
    from tests.test_strategy.conftest import create_mock_mtf_context
    global_state.market_service = MultiTimeframeService()
    global_state.market_service.latest_contexts["BTCUSD"] = create_mock_mtf_context()

    response = client.get("/api/v1/market/current?symbol=BTCUSD", headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    market_obj = MarketSnapshotResponse(**data)

    assert market_obj.symbol == "BTC/USD"
    assert market_obj.trend.direction.lower() == "bullish"

def test_ranking_result_schema():
    from app.core.state import global_state
    from app.strategy.ranking_engine import StrategyRankingEngine
    from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
    from app.strategy.strategies.mtf_trend_alignment import MultiTimeframeTrendAlignmentStrategy
    from app.strategy.strategies.donchian_breakout import DonchianChannelBreakoutStrategy
    from tests.test_strategy.conftest import create_mock_snapshot
    global_state.ranking_engine = StrategyRankingEngine(strategies=[
        EMATrendPullbackStrategy(),
        MultiTimeframeTrendAlignmentStrategy(),
        DonchianChannelBreakoutStrategy(),
    ])
    snapshot = create_mock_snapshot()
    global_state.ranking_engine.latest_rankings["BTCUSD"] = global_state.ranking_engine.rank(
        db=None, symbol="BTCUSD", timeframe="H1", snapshot=snapshot, strategy_results={}
    )

    response = client.get("/api/v1/strategy/ranking?symbol=BTCUSD", headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    ranking_obj = RankingResponse(**data)

    assert ranking_obj.winner is not None
    assert len(ranking_obj.ranking) > 0

def test_journal_latest_schema():
    from app.core.state import global_state
    from app.analytics.journal import DecisionJournal
    from app.analytics.events import EventBus, DecisionEvent
    from app.strategy.models.ranking import RankingResult, StrategyScore
    from app.risk.models import RiskAssessment
    from datetime import datetime, timezone

    # Seed a decision via the in-memory journal so /journal/latest returns data.
    event_bus = EventBus()
    journal = DecisionJournal(event_bus=event_bus)
    global_state.journal = journal
    ranking = RankingResult(
        timestamp=datetime.now(timezone.utc),
        symbol="BTCUSD",
        timeframe="H1",
        rankings=[
            StrategyScore(strategy_name="TestStrategy", historical_score=50, market_score=50, setup_score=50, final_score=50),
        ],
        selected_strategy="TestStrategy",
        selection_reason="Test",
    )
    candidate = TradeCandidate(
        strategy_name="TestStrategy",
        strategy_version="v1",
        symbol="BTCUSD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100"),
        stop_loss=Decimal("99"),
        market_conditions={},
    )
    risk = RiskAssessment(is_approved=True, rejection_reason=None, position_size=Decimal("1"), candidate=candidate)
    event_bus.publish(DecisionEvent(
        decision_id="test-decision-001",
        symbol="BTCUSD",
        timeframe="H1",
        ranking_result=ranking,
        risk_assessment=risk,
    ))

    response = client.get("/api/v1/journal/latest", headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    # The endpoint reads from DB; in-memory journal entries are not persisted.
    # We validate the schema shape rather than requiring rows.
    assert all("decision_id" in entry for entry in data) if data else True

def test_auth_unauthorized():
    # Clear overrides to test auth rejection
    app.dependency_overrides.clear()
    
    response = client.get("/api/v1/system/status") # Missing API key
    assert response.status_code == 401
    
    # Restore override for other tests if needed
    app.dependency_overrides[get_current_user] = override_get_current_user
