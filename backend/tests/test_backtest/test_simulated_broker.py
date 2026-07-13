import pytest
from decimal import Decimal
from datetime import datetime

from app.backtest.models import BacktestConfig
from app.backtest.simulated_broker import SimulatedBroker
from app.strategy.models import TradeCandidate, TradeDirection
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.risk.models import RiskProfile

def test_entry_price_includes_slippage():
    config = BacktestConfig(
        strategy_id="test",
        strategy_version="1.0",
        instrument="BTC/USD",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 2),
        initial_balance=Decimal("10000.00"),
        commission=Decimal("5.0"),
        spread=Decimal("2.0"),
        slippage=Decimal("1.0")
    )
    profile = RiskProfile(account_balance=Decimal("10000.00"), risk_per_trade_percent=Decimal("1.0"))
    broker = SimulatedBroker(config, profile)
    
    candidate = TradeCandidate(
        strategy_name="test",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("90.0"),
        take_profit=Decimal("120.0"),
        market_conditions={}
    )
    
    # 1. Submit Candidate
    broker.submit_candidate(candidate, datetime(2025, 1, 1, 10, 0))
    
    assert len(broker.active_positions) == 1
    pos = broker.active_positions[0]
    
    # Expected fill price: 100.0 + (spread/2) + slippage
    # = 100.0 + 1.0 + 1.0 = 102.0
    assert pos.entry_price == Decimal("102.0")
    
    # Verify commission deducted from balance
    assert broker.balance == Decimal("9995.0")

def test_intra_bar_sl_execution():
    config = BacktestConfig(
        strategy_id="test",
        strategy_version="1.0",
        instrument="BTC/USD",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 2),
        initial_balance=Decimal("10000.00"),
        commission=Decimal("0.0"),
        spread=Decimal("0.0"),
        slippage=Decimal("0.0")
    )
    profile = RiskProfile(account_balance=Decimal("10000.00"), risk_per_trade_percent=Decimal("1.0"))
    broker = SimulatedBroker(config, profile)
    
    candidate = TradeCandidate(
        strategy_name="test",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("98.0"),
        take_profit=Decimal("104.0"),
        market_conditions={}
    )
    
    broker.submit_candidate(candidate, datetime(2025, 1, 1, 10, 0))
    
    # Simulate a 1M candle that hits SL
    candle = Candle(
        instrument="BTC/USD",
        timeframe=Timeframe.M1,
        timestamp=datetime(2025, 1, 1, 10, 3),
        open=Decimal("100.5"),
        high=Decimal("103.0"),
        low=Decimal("97.0"),
        close=Decimal("102.0"),
        volume=Decimal("10"),
        source="test"
    )
    
    broker.process_1m_candle(candle)
    
    assert len(broker.active_positions) == 0
    assert len(broker.closed_trades) == 1
    
    trade = broker.closed_trades[0]
    assert trade.reason == "STOP_LOSS"
    assert trade.exit_price == Decimal("98.0")
