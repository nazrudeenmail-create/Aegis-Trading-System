import pytest
from decimal import Decimal
from datetime import datetime

from app.backtest.models import BacktestConfig
from app.backtest.simulated_broker import SimulatedBroker
from app.backtest.engine import BacktestEngine
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.risk.models import RiskProfile

from app.strategy.base import BaseStrategy

# Dummy strategy that just records when it was evaluated
class DummyStrategy(BaseStrategy):
    name = "Dummy"
    version = "1.0"
    description = "Dummy strategy for backtest engine tests"
    primary_timeframe = Timeframe.M15
    required_timeframes = [Timeframe.M15]
    
    def __init__(self):
        self.evaluation_times = []
        
    def get_profile(self):
        from app.strategy.models.ranking import StrategyProfile
        return StrategyProfile()
        
    def evaluate(self, context):
        self.evaluation_times.append(context.timestamp)
        from app.strategy.models import StrategyResult
        return StrategyResult(is_valid=False, rejection_reason="Dummy")

def test_strategy_cannot_use_future_candle():
    config = BacktestConfig(
        strategy_id="dummy",
        strategy_version="1.0",
        instrument="BTC/USD",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 2),
        initial_balance=Decimal("10000.00")
    )
    profile = RiskProfile(account_balance=Decimal("10000.00"), risk_per_trade_percent=Decimal("1.0"))
    broker = SimulatedBroker(config, profile)
    strategy = DummyStrategy()
    
    engine = BacktestEngine(config, broker, strategy)
    
    # Create 1M candles from 10:00 to 10:15
    candles = []
    for i in range(16): # 10:00 to 10:15 inclusive
        candles.append(Candle(
            instrument="BTC/USD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, 10, i),
            open=Decimal("100.0"),
            high=Decimal("100.0"),
            low=Decimal("100.0"),
            close=Decimal("100.0"),
            volume=Decimal("10"),
            source="test"
        ))
        
    engine.run(candles)
    
    # The 15M candle closes after the 10:14 1M candle finishes.
    # Therefore, evaluate() should have been called precisely once at 10:14.
    assert len(strategy.evaluation_times) == 1
    assert strategy.evaluation_times[0] == datetime(2025, 1, 1, 10, 14)
