import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.strategy.models.ranking import StrategyProfile
from app.market_analysis.models import MarketRegime, MarketSnapshot
from app.database.models import BacktestRun, Account
from app.database.enums import AccountType
from app.strategy.scoring.historical import HistoricalScorer
from app.strategy.scoring.compatibility import CompatibilityScorer
from app.strategy.scoring.setup import SetupScorer
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection
from app.strategy.ranking_engine import StrategyRankingEngine

class MockStrategy:
    def __init__(self, name, profile):
        self.name = name
        self.profile = profile
    def get_profile(self):
        return self.profile

@pytest.fixture
def db_session():
    # We need a mock db session or we can just mock the query.
    class MockQuery:
        def __init__(self, runs):
            self.runs = runs
        def filter(self, *args):
            return self
        def order_by(self, *args):
            return self
        def first(self):
            return self.runs[0] if self.runs else None
            
    class MockDB:
        def __init__(self):
            self.runs = []
        def query(self, model):
            return MockQuery(self.runs)
            
    return MockDB()

def test_low_trade_count_penalty(db_session):
    db_session.runs = [
        BacktestRun(
            strategy_name="A",
            total_trades=20,
            win_rate=80.0,
            profit_factor=Decimal("3.0"),
            expectancy=Decimal("5.0"),
            max_drawdown=Decimal("5.0"),
            end_date=datetime.now(timezone.utc)
        )
    ]
    scorer = HistoricalScorer()
    score_20 = scorer.score(db_session, "A")
    
    db_session.runs = [
        BacktestRun(
            strategy_name="B",
            total_trades=2000,
            win_rate=65.0,
            profit_factor=Decimal("1.5"),
            expectancy=Decimal("2.0"),
            max_drawdown=Decimal("10.0"),
            end_date=datetime.now(timezone.utc)
        )
    ]
    score_2000 = scorer.score(db_session, "B")
    
    # Even though A has better raw stats, B should have a higher score due to sample size.
    assert score_20 < score_2000

def test_historical_recency(db_session):
    # Same stats, different end dates
    db_session.runs = [
        BacktestRun(
            strategy_name="Recent",
            total_trades=1000,
            win_rate=65.0,
            profit_factor=Decimal("1.5"),
            expectancy=Decimal("2.0"),
            max_drawdown=Decimal("10.0"),
            end_date=datetime.now(timezone.utc)
        )
    ]
    scorer = HistoricalScorer()
    score_recent = scorer.score(db_session, "Recent")
    
    db_session.runs = [
        BacktestRun(
            strategy_name="Old",
            total_trades=1000,
            win_rate=65.0,
            profit_factor=Decimal("1.5"),
            expectancy=Decimal("2.0"),
            max_drawdown=Decimal("10.0"),
            end_date=datetime.now(timezone.utc) - timedelta(days=1200) # > 3 years
        )
    ]
    score_old = scorer.score(db_session, "Old")
    
    assert score_recent > score_old
    assert score_old == score_recent * 0.5 # Since penalty is 0.5 for > 3 years

def test_no_trade_candidate():
    result = StrategyResult(is_valid=False, rejection_reason="No setup")
    setup_score = SetupScorer.score("A", result)
    assert not setup_score.has_setup
    assert setup_score.confidence == 0.0

def test_trend_strategy_compatibility():
    profile = StrategyProfile(
        name="Trend",
        preferred_regimes=[MarketRegime.TRENDING],
        acceptable_regimes=[MarketRegime.BREAKOUT],
        avoided_regimes=[MarketRegime.RANGING],
        preferred_timeframes=[],
        volatility_preference="Normal"
    )
    
    from app.market_analysis.models import MarketRegimeAnalysis
    
    trending_snapshot = MarketSnapshot(
        regime=MarketRegimeAnalysis(regime=MarketRegime.TRENDING)
    )
    score_trend = CompatibilityScorer.score(profile, trending_snapshot)
    
    ranging_snapshot = MarketSnapshot(
        regime=MarketRegimeAnalysis(regime=MarketRegime.RANGING)
    )
    score_range = CompatibilityScorer.score(profile, ranging_snapshot)
    
    assert score_trend == 100.0
    assert score_range == 40.0 # 100 * 0.40 avoided penalty

def test_ranking_explainability(db_session):
    profile = StrategyProfile(
        name="Trend",
        preferred_regimes=[MarketRegime.TRENDING],
        acceptable_regimes=[],
        avoided_regimes=[],
        preferred_timeframes=[],
        volatility_preference=""
    )
    strategy = MockStrategy("Trend", profile)
    engine = StrategyRankingEngine(strategies=[strategy])
    
    # Mock DB run
    db_session.runs = [
        BacktestRun(
            strategy_name="Trend",
            total_trades=1000,
            win_rate=80.0,
            profit_factor=Decimal("2.0"),
            expectancy=Decimal("5.0"),
            max_drawdown=Decimal("5.0"),
            end_date=datetime.now(timezone.utc)
        )
    ]
    
    from app.market_analysis.models import MarketRegimeAnalysis
    snapshot = MarketSnapshot(
        regime=MarketRegimeAnalysis(regime=MarketRegime.TRENDING)
    )
    
    candidate = TradeCandidate(
        strategy_name="Trend",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100"),
        stop_loss=Decimal("90"),
        market_conditions={}
    )
    # Add confidence
    candidate.confidence = 80.0
    
    results = {"Trend": StrategyResult(is_valid=True, candidate=candidate)}
    
    ranking = engine.rank(db_session, "BTC/USD", "H1", snapshot, results)
    
    assert ranking.selected_strategy == "Trend"
    assert "Historical:" in ranking.selection_reason
    assert "Compatibility:" in ranking.selection_reason
    assert "Setup:" in ranking.selection_reason
