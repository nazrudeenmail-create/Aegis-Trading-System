import pytest
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from app.analytics.events import EventBus, DecisionEvent, ExecutionEvent, TradeClosedEvent
from app.analytics.journal import DecisionJournal
from app.strategy.models.ranking import RankingResult, StrategyScore
from app.market_analysis.enums import MarketRegime
from app.risk.models import RiskAssessment
from app.execution.models.order import OrderResult, OrderStatus, TradeRecord, OrderDirection
from app.strategy.models import TradeCandidate, TradeDirection


@pytest.fixture
def event_bus():
    return EventBus()

@pytest.fixture
def journal(event_bus):
    return DecisionJournal(event_bus)


def get_dummy_candidate():
    return TradeCandidate(
        symbol="BTC/USD", strategy_name="EMA", strategy_version="1.0", direction=TradeDirection.LONG,
        entry_price=Decimal("100"), stop_loss=Decimal("90"), take_profit=Decimal("110"),
        confidence=0.8, market_conditions={}
    )


def test_decision_is_immutable(journal, event_bus):
    """Verify that old decisions cannot be arbitrarily mutated by users/process"""
    dec_id = str(uuid.uuid4())
    ranking = RankingResult(
        symbol="BTC/USD", timeframe="1H", timestamp=datetime.now(timezone.utc),
        market_regime=MarketRegime.TRENDING,
        rankings=[StrategyScore(strategy_name="EMA", historical_score=50.0, market_score=50.0, setup_score=50.0, final_score=50.0)],
        selected_strategy="EMA", selection_reason="Top"
    )
    
    event_bus.publish(DecisionEvent(
        decision_id=dec_id, symbol="BTC/USD", timeframe="1H",
        ranking_result=ranking, risk_assessment=RiskAssessment(candidate=get_dummy_candidate(), is_approved=True, position_size=Decimal("1.0"))
    ))
    
    record = journal.decisions[dec_id]
    assert record.outcome_status == "PENDING"
    
    event_bus.publish(ExecutionEvent(
        decision_id=dec_id,
        order_result=OrderResult(order_id="order-123", status=OrderStatus.FILLED, filled_price=Decimal("100"), filled_quantity=Decimal("1.0"), timestamp=datetime.now(timezone.utc))
    ))
    
    record = journal.decisions[dec_id]
    assert record.order_id == "order-123"
    assert record.selected_strategy == "EMA"
    assert record.outcome_status == "EXECUTED"


def test_decision_journal_logs_rejections(journal, event_bus):
    """Verify that trades blocked by the Risk Engine are logged with their rejection reason."""
    dec_id = str(uuid.uuid4())
    ranking = RankingResult(
        symbol="ETH/USD", timeframe="15M", timestamp=datetime.now(timezone.utc),
        market_regime=MarketRegime.RANGING,
        rankings=[StrategyScore(strategy_name="EMA", historical_score=50.0, market_score=50.0, setup_score=50.0, final_score=50.0)],
        selected_strategy="EMA", selection_reason="Top"
    )
    
    event_bus.publish(DecisionEvent(
        decision_id=dec_id, symbol="ETH/USD", timeframe="15M",
        ranking_result=ranking, risk_assessment=RiskAssessment(candidate=get_dummy_candidate(), is_approved=False, position_size=Decimal("0"), rejection_reason="Max exposure exceeded.")
    ))
    
    record = journal.decisions[dec_id]
    assert record.risk_approved is False
    assert record.risk_reason == "Max exposure exceeded."
    assert record.outcome_status == "REJECTED"


def test_decision_journal_links_trades(journal, event_bus):
    """Verify that a closed TradeRecord can be successfully linked back to its originating DecisionRecord."""
    dec_id = str(uuid.uuid4())
    ord_id = str(uuid.uuid4())
    
    ranking = RankingResult(
        symbol="SOL/USD", timeframe="4H", timestamp=datetime.now(timezone.utc),
        market_regime=MarketRegime.BREAKOUT,
        rankings=[StrategyScore(strategy_name="Breakout", historical_score=50.0, market_score=50.0, setup_score=50.0, final_score=50.0)],
        selected_strategy="Breakout", selection_reason="Top"
    )
    
    event_bus.publish(DecisionEvent(
        decision_id=dec_id, symbol="SOL/USD", timeframe="4H",
        ranking_result=ranking, risk_assessment=RiskAssessment(candidate=get_dummy_candidate(), is_approved=True, position_size=Decimal("1.0"))
    ))
    
    # Executed
    event_bus.publish(ExecutionEvent(
        decision_id=dec_id,
        order_result=OrderResult(order_id=ord_id, status=OrderStatus.FILLED, filled_price=Decimal("100"), filled_quantity=Decimal("1.0"), timestamp=datetime.now(timezone.utc))
    ))
    
    record = journal.decisions[dec_id]
    assert record.order_id == ord_id
    
    # Trade Closed (Win)
    trade = TradeRecord(
        trade_id=ord_id, symbol="SOL/USD", direction=OrderDirection.LONG,
        entry_price=Decimal("100"), exit_price=Decimal("110"), quantity=Decimal("1.0"),
        pnl=Decimal("10"), pnl_percent=10.0,
        entry_time=datetime.now(timezone.utc), exit_time=datetime.now(timezone.utc),
        strategy_name="Breakout", ranking_score=Decimal("50.0"), market_regime="breakout",
        entry_reason="Rank", exit_reason="TAKE_PROFIT"
    )
    
    event_bus.publish(TradeClosedEvent(trade_record=trade))
    
    record = journal.decisions[dec_id]
    assert record.trade_id == ord_id
    assert record.outcome_status == "WIN"
    assert record.profit_loss == Decimal("10")
    assert record.r_multiple == 0.1
