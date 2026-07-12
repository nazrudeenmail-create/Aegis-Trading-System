import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone

from app.strategy.models import TradeCandidate, TradeDirection
from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.execution.models.paper_config import PaperTradingConfig, ExecutionSimulationConfig
from app.execution.models.order import OrderRequest, OrderDirection, OrderType, OrderStatus
from app.execution.models.validation_report import PaperTradingStatus
from app.execution.broker.paper_broker import PaperBroker
from app.execution.engine import ExecutionEngine
from app.execution.paper_monitor import PaperTradingMonitor


@pytest.fixture
def sim_config():
    return ExecutionSimulationConfig(
        slippage_enabled=False,
        commission_enabled=False,
        execution_delay_ms=0
    )


@pytest.fixture
def broker(sim_config):
    b = PaperBroker(initial_balance=Decimal("10000.0"), config=sim_config)
    asyncio.run(b.connect())
    return b


@pytest.fixture
def candidate():
    return TradeCandidate(
        strategy_name="Test Strategy",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("60000.0"),
        stop_loss=Decimal("59000.0"),
        take_profit=Decimal("62000.0"),
        market_conditions={"regime": "TRENDING", "adx": 30.0}
    )


@pytest.fixture
def risk_profile():
    return RiskProfile(
        account_balance=Decimal("10000.0"),
        max_risk_per_trade_percent=Decimal("1.0"),
        max_open_risk_percent=Decimal("3.0"),
        max_daily_loss_percent=Decimal("5.0")
    )


@pytest.mark.asyncio
async def test_paper_broker_fill(broker):
    broker.tick("BTC/USD", price=Decimal("60000.0"), timestamp=datetime.now(timezone.utc))
    
    order = OrderRequest(
        symbol="BTC/USD",
        direction=OrderDirection.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0")
    )
    result = await broker.place_order(order)
    
    assert result.status == OrderStatus.FILLED
    assert result.filled_price == Decimal("60000.0")
    assert result.filled_quantity == Decimal("1.0")
    assert "BTC/USD" in broker.positions


@pytest.mark.asyncio
async def test_paper_trade_stop_loss_execution(broker):
    ts = datetime.now(timezone.utc)
    broker.tick("BTC/USD", price=Decimal("60000.0"), timestamp=ts)
    
    order = OrderRequest(
        symbol="BTC/USD",
        direction=OrderDirection.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0")
    )
    await broker.place_order(order)
    
    # Set SL
    pos = broker.positions["BTC/USD"]
    pos.stop_loss = Decimal("59000.0")
    
    # Hit SL
    broker.tick("BTC/USD", price=Decimal("58000.0"), timestamp=ts)
    
    assert "BTC/USD" not in broker.positions
    assert len(broker.closed_trades) == 1
    assert broker.closed_trades[0].exit_reason == "STOP_LOSS"
    assert broker.closed_trades[0].pnl < 0


@pytest.mark.asyncio
async def test_execution_engine_risk_rejection(broker, candidate, risk_profile):
    risk_engine = RiskEngine()
    engine = ExecutionEngine(broker, risk_engine)
    
    # Force rejection by passing candidate with 0 SL distance
    bad_candidate = TradeCandidate(
        strategy_name="Test",
        strategy_version="1",
        symbol="TEST",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100"),
        stop_loss=Decimal("100"), # Zero distance -> Rejected
        take_profit=Decimal("110"),
        market_conditions={}
    )
    
    result = await engine.execute(bad_candidate, 90.0, risk_profile, risk_context={"current_open_risk_fiat": Decimal("0.0"), "daily_loss_fiat": Decimal("0.0"), "account_balance": Decimal("10000")})
    assert result is None
    assert len(broker.positions) == 0


@pytest.mark.asyncio
async def test_execution_engine_success(broker, candidate, risk_profile):
    risk_engine = RiskEngine()
    engine = ExecutionEngine(broker, risk_engine)
    
    broker.tick("BTC/USD", price=Decimal("60000.0"), timestamp=datetime.now(timezone.utc))
    
    result = await engine.execute(candidate, 85.0, risk_profile, risk_context={"current_open_risk_fiat": Decimal("0.0"), "daily_loss_fiat": Decimal("0.0"), "account_balance": Decimal("10000")})
    
    assert result is not None
    assert result.status == OrderStatus.FILLED
    pos = broker.positions["BTC/USD"]
    assert pos.stop_loss == Decimal("59000.0")
    assert pos.strategy_name == "Test Strategy"


def test_paper_duration_tracking(broker, candidate):
    config = PaperTradingConfig(max_duration_days=10, required_trade_count=50)
    monitor = PaperTradingMonitor(config)
    
    # Force trade
    ts = datetime.now(timezone.utc)
    broker.tick("BTC/USD", price=Decimal("60000.0"), timestamp=ts)
    order = OrderRequest(symbol="BTC/USD", direction=OrderDirection.LONG, order_type=OrderType.MARKET, quantity=Decimal("1.0"))
    asyncio.run(broker.place_order(order))
    
    pos = broker.positions["BTC/USD"]
    pos.strategy_name = "Test Strategy"
    pos.take_profit = Decimal("62000.0")
    broker.tick("BTC/USD", price=Decimal("63000.0"), timestamp=ts)
    
    report = monitor.generate_report("Test Strategy", broker.closed_trades, days_running=5)
    assert report.status == PaperTradingStatus.ACTIVE
    
    report = monitor.generate_report("Test Strategy", broker.closed_trades, days_running=10)
    assert report.status == PaperTradingStatus.FAILED_VALIDATION


def test_user_controls_validation_period(broker):
    # Ensure ATS doesn't automatically move to USER_APPROVED
    config = PaperTradingConfig(required_trade_count=100)
    monitor = PaperTradingMonitor(config)
    
    report = monitor.generate_report("Test Strategy", [], days_running=30)
    assert report.status != PaperTradingStatus.USER_APPROVED


def test_monitor_strategy_attribution(broker):
    ts = datetime.now(timezone.utc)
    broker.tick("BTC/USD", price=Decimal("60000.0"), timestamp=ts)
    asyncio.run(broker.place_order(OrderRequest(symbol="BTC/USD", direction=OrderDirection.LONG, order_type=OrderType.MARKET, quantity=Decimal("1.0"))))
    
    pos = broker.positions["BTC/USD"]
    pos.strategy_name = "Alpha"
    pos.ranking_score = Decimal("95.5")
    pos.market_regime = "TRENDING"
    
    # Close it
    broker.tick("BTC/USD", price=Decimal("61000.0"), timestamp=ts)
    asyncio.run(broker.place_order(OrderRequest(symbol="BTC/USD", direction=OrderDirection.SHORT, order_type=OrderType.MARKET, quantity=Decimal("1.0"))))
    
    assert len(broker.closed_trades) == 1
    trade = broker.closed_trades[0]
    assert trade.strategy_name == "Alpha"
    assert trade.ranking_score == Decimal("95.5")
    assert trade.market_regime == "TRENDING"
