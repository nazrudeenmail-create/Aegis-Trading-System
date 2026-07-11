import pytest
from decimal import Decimal
from app.risk.models import RiskProfile
from app.strategy.models import TradeCandidate, TradeDirection
from app.risk.engine import RiskEngine

@pytest.fixture
def profile():
    return RiskProfile(
        account_balance=Decimal("10000.0"),
        risk_per_trade_percent=Decimal("1.0"),
        max_open_risk_percent=Decimal("5.0"),
        max_daily_drawdown_percent=Decimal("3.0")
    )

@pytest.fixture
def candidate():
    return TradeCandidate(
        strategy_name="Test",
        strategy_version="1.0",
        symbol="BTCUSDT",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("95.0"),
        market_conditions={}
    )

def test_engine_approve(profile, candidate):
    engine = RiskEngine()
    context = {'current_open_risk_fiat': Decimal("0.0"), 'daily_loss_fiat': Decimal("0.0")}
    assessment = engine.evaluate(candidate, profile, context)
    
    assert assessment.is_approved is True
    assert assessment.position_size == Decimal("20.0")
    assert assessment.risk_amount_fiat == Decimal("100.0")
    assert assessment.approved_risk_percent == Decimal("1.0")

def test_engine_reject_exposure(profile, candidate):
    engine = RiskEngine()
    # 500 max open risk. Current is 450. Trade needs 100. Should reject.
    context = {'current_open_risk_fiat': Decimal("450.0"), 'daily_loss_fiat': Decimal("0.0")}
    assessment = engine.evaluate(candidate, profile, context)
    
    assert assessment.is_approved is False
    assert "Exposure limit breached" in assessment.rejection_reason
    assert assessment.position_size == Decimal("0.0")
    assert assessment.risk_amount_fiat == Decimal("0.0")

def test_engine_reject_daily_loss(profile, candidate):
    engine = RiskEngine()
    # 300 max daily loss. Current is 350.
    context = {'current_open_risk_fiat': Decimal("0.0"), 'daily_loss_fiat': Decimal("350.0")}
    assessment = engine.evaluate(candidate, profile, context)
    
    assert assessment.is_approved is False
    assert "Daily drawdown limit reached" in assessment.rejection_reason

def test_engine_allow_high_risk(candidate):
    profile = RiskProfile(
        account_balance=Decimal("10000.0"),
        max_open_risk_percent=Decimal("3.0"),
        allow_high_risk_mode=True
    )
    engine = RiskEngine()
    # Max risk = 300. We want to add 100. Current is 250. Total = 350.
    # Should warn and approve.
    context = {'current_open_risk_fiat': Decimal("250.0"), 'daily_loss_fiat': Decimal("0.0")}
    assessment = engine.evaluate(candidate, profile, context)
    
    assert assessment.is_approved is True
    assert len(assessment.warnings) > 0
    assert "Bypassed exposure limit" in assessment.warnings[0]
