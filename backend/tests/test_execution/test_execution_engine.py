"""Tests for ExecutionEngine emergency stop and readiness gate."""
import pytest
from decimal import Decimal

from app.execution.engine import ExecutionEngine
from app.execution.broker.manager import BrokerManager
from app.execution.broker.models import ConnectionState
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderResult, OrderStatus
from app.core.state import global_state, SystemState, SystemStateEnum
from app.strategy.models import TradeCandidate, TradeDirection
from app.strategy.models.ranking import RankingResult
from app.risk.models import RiskProfile, RiskAssessment
from app.analytics.events import EventBus


class FakeBrokerManager(BrokerManager):
    def __init__(self):
        super().__init__()
        self.last_order = None

    async def place_order(self, order: OrderRequest) -> OrderResult:
        self.last_order = order
        return OrderResult(
            order_id="FAKE1",
            status=OrderStatus.FILLED,
            filled_price=Decimal("100"),
            filled_quantity=order.quantity,
        )


class FakeRiskEngine:
    def evaluate(self, candidate, profile, context):
        return RiskAssessment(
            is_approved=True,
            rejection_reason=None,
            position_size=Decimal("1.0"),
            candidate=candidate,
        )


@pytest.fixture
def engine():
    broker_manager = FakeBrokerManager()
    broker_manager.state = ConnectionState.CONNECTED
    risk_engine = FakeRiskEngine()
    event_bus = EventBus()
    return ExecutionEngine(broker_manager, risk_engine, event_bus)


@pytest.fixture
def candidate():
    return TradeCandidate(
        strategy_name="Test",
        strategy_version="1.0",
        symbol="EURUSD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100"),
        stop_loss=Decimal("99"),
        market_conditions={"timeframe": "H1"},
    )


@pytest.fixture
def ranking_result():
    from datetime import datetime, timezone
    return RankingResult(
        timestamp=datetime.now(timezone.utc),
        symbol="EURUSD",
        timeframe="H1",
        rankings=[],
        selected_strategy="Test",
        selection_reason="Test",
    )


@pytest.mark.asyncio
async def test_execution_rejected_when_halted(engine, candidate, ranking_result):
    global_state.system_state = SystemState(SystemStateEnum.HALTED)
    # Provide minimal global state so readiness failure is not the first blocker.
    global_state.market_service = object()
    global_state.ranking_engine = object()
    global_state.risk_engine = object()

    result = await engine.execute(
        candidate,
        ranking_result,
        RiskProfile(account_balance=Decimal("10000"), risk_per_trade_percent=Decimal("1")),
        {},
    )

    assert result is None


@pytest.mark.asyncio
async def test_execution_rejected_when_readiness_fails(engine, candidate, ranking_result):
    global_state.system_state = SystemState(SystemStateEnum.ACTIVE)
    # Leave global engines unset so readiness fails.
    global_state.market_service = None
    global_state.ranking_engine = None
    global_state.risk_engine = None

    result = await engine.execute(
        candidate,
        ranking_result,
        RiskProfile(account_balance=Decimal("10000"), risk_per_trade_percent=Decimal("1")),
        {},
    )

    assert result is None


@pytest.mark.asyncio
async def test_execution_succeeds_when_ready(engine, candidate, ranking_result):
    global_state.system_state = SystemState(SystemStateEnum.ACTIVE)
    global_state.market_service = object()
    global_state.ranking_engine = object()
    global_state.risk_engine = engine.risk_engine

    result = await engine.execute(
        candidate,
        ranking_result,
        RiskProfile(account_balance=Decimal("10000"), risk_per_trade_percent=Decimal("1")),
        {},
    )

    assert result is not None
    assert result.status == OrderStatus.FILLED
    assert engine.broker_manager.last_order is not None
    assert engine.broker_manager.last_order.order_type == OrderType.MARKET
