import pytest
from decimal import Decimal
from app.risk.calculator import PositionCalculator
from app.risk.models import RiskProfile
from app.strategy.models import TradeCandidate, TradeDirection

@pytest.fixture
def base_candidate():
    return TradeCandidate(
        strategy_name="Test",
        strategy_version="1.0",
        symbol="BTCUSDT",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("95.0"),
        market_conditions={}
    )

@pytest.fixture
def profile():
    return RiskProfile(
        account_balance=Decimal("10000.0"),
        risk_per_trade_percent=Decimal("1.0")
    )

def test_long_position_size(base_candidate, profile):
    # Entry: 100, Stop: 95. Distance = 5.
    # Risk: 1% of 10000 = 100.
    # Position: 100 / 5 = 20
    calc = PositionCalculator()
    size, risk, percent = calc.calculate_position(base_candidate, profile)
    
    assert size == Decimal("20.0")
    assert risk == Decimal("100.0")
    assert percent == Decimal("1.0")

def test_short_position_size(base_candidate, profile):
    base_candidate.direction = TradeDirection.SHORT
    base_candidate.entry_price = Decimal("100.0")
    base_candidate.stop_loss = Decimal("105.0")
    # Distance = 5. Risk = 100. Size = 20.
    calc = PositionCalculator()
    size, risk, percent = calc.calculate_position(base_candidate, profile)
    
    assert size == Decimal("20.0")
    assert risk == Decimal("100.0")

def test_zero_stop_loss_distance(base_candidate, profile):
    base_candidate.stop_loss = Decimal("100.0")
    calc = PositionCalculator()
    size, risk, percent = calc.calculate_position(base_candidate, profile)
    
    assert size == Decimal("0")
    assert risk == Decimal("0")
