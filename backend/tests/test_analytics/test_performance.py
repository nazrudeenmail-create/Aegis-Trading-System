from app.market.domain.timeframe import Timeframe
import pytest
from datetime import datetime, timezone
from decimal import Decimal

from app.analytics.models import DecisionRecord, StrategyScoreRecord
from app.analytics.performance import AnalyticsEngine


@pytest.fixture
def mock_decisions():
    ts = datetime.now(timezone.utc)
    
    # 1. EMA Win (Trending) - 90% confidence
    d1 = DecisionRecord(
        decision_id="1", timestamp=ts, symbol="BTC/USD", timeframe=Timeframe.H1, market_regime="trending",
        strategies_considered=[], selected_strategy="EMA",
        confidence_score=90.0,
        outcome_status="WIN", profit_loss=Decimal("100")
    )
    
    # 2. EMA Loss (Trending) - 60% confidence
    d2 = DecisionRecord(
        decision_id="2", timestamp=ts, symbol="BTC/USD", timeframe=Timeframe.H1, market_regime="trending",
        strategies_considered=[], selected_strategy="EMA",
        confidence_score=60.0,
        outcome_status="LOSS", profit_loss=Decimal("-50")
    )
    
    # 3. Donchian Win (Ranging) - 80% confidence
    d3 = DecisionRecord(
        decision_id="3", timestamp=ts, symbol="ETH/USD", timeframe=Timeframe.H1, market_regime="ranging",
        strategies_considered=[], selected_strategy="Donchian",
        confidence_score=80.0,
        outcome_status="WIN", profit_loss=Decimal("200")
    )
    
    # 4. Rejected Trade (No outcome)
    d4 = DecisionRecord(
        decision_id="4", timestamp=ts, symbol="ETH/USD", timeframe=Timeframe.H1, market_regime="ranging",
        strategies_considered=[], selected_strategy="Donchian",
        confidence_score=80.0,
        outcome_status="REJECTED", profit_loss=None
    )
    
    return [d1, d2, d3, d4]


def test_performance_analytics_by_strategy(mock_decisions):
    """Verify accurate Expectancy and Profit Factor calculations."""
    stats = AnalyticsEngine.calculate_strategy_performance(mock_decisions)
    
    assert "EMA" in stats
    assert "Donchian" in stats
    
    ema = stats["EMA"]
    assert ema.total_trades == 2
    assert ema.winning_trades == 1
    assert ema.losing_trades == 1
    assert ema.win_rate == 50.0
    assert ema.net_profit == Decimal("50")
    assert ema.profit_factor == 2.0  # $100 / $50
    
    don = stats["Donchian"]
    assert don.total_trades == 1
    assert don.winning_trades == 1
    assert don.win_rate == 100.0


def test_performance_analytics_by_regime(mock_decisions):
    """Verify analytics segmentation by Market Regime."""
    regimes = AnalyticsEngine.calculate_regime_performance(mock_decisions)
    
    assert "trending" in regimes
    assert "ranging" in regimes
    
    trending = regimes["trending"]
    assert trending.total_trades == 2
    assert trending.win_rate == 50.0
    assert trending.net_profit == Decimal("50")
    
    ranging = regimes["ranging"]
    assert ranging.total_trades == 1
    assert ranging.win_rate == 100.0
    assert ranging.net_profit == Decimal("200")


def test_ranking_decision_accuracy_tracking(mock_decisions):
    """Verify ranking accuracy metrics."""
    acc = AnalyticsEngine.calculate_ranking_accuracy(mock_decisions)
    
    assert acc.total_decisions == 3  # 3 executed trades
    assert acc.profitable_decisions == 2 # 2 wins
    assert round(acc.accuracy_percent, 2) == 66.67


def test_confidence_calibration(mock_decisions):
    """Verify confidence buckets calculate win rates properly."""
    cal = AnalyticsEngine.calculate_confidence_calibration(mock_decisions)
    
    # 60% confidence -> 51-75% bucket -> LOSS
    # 80% confidence -> 76-100% bucket -> WIN
    # 90% confidence -> 76-100% bucket -> WIN
    
    bucket_51_75 = next(b for b in cal if b.confidence_bucket == "51-75%")
    assert bucket_51_75.total_trades == 1
    assert bucket_51_75.win_rate == 0.0
    
    bucket_76_100 = next(b for b in cal if b.confidence_bucket == "76-100%")
    assert bucket_76_100.total_trades == 2
    assert bucket_76_100.win_rate == 100.0
