import pytest
from decimal import Decimal
from app.risk.models import RiskProfile
from app.risk.validator import RiskProfileValidator, ExposureValidator, DailyLossValidator

@pytest.fixture
def profile():
    return RiskProfile(
        account_balance=Decimal("10000.0"),
        risk_per_trade_percent=Decimal("1.0"),
        max_open_risk_percent=Decimal("5.0"),
        max_daily_drawdown_percent=Decimal("3.0")
    )

def test_risk_profile_validator_normal(profile):
    validator = RiskProfileValidator()
    result = validator.validate(profile, {})
    assert result.is_valid is True

def test_risk_profile_validator_high_risk_rejected():
    profile = RiskProfile(
        account_balance=Decimal("10000.0"),
        risk_per_trade_percent=Decimal("10.0"), # high
        allow_high_risk_mode=False
    )
    validator = RiskProfileValidator()
    result = validator.validate(profile, {})
    assert result.is_valid is False
    assert "Risk per trade exceeds 5%" in result.reason

def test_risk_profile_validator_high_risk_allowed():
    profile = RiskProfile(
        account_balance=Decimal("10000.0"),
        max_open_risk_percent=Decimal("30.0"), # high
        allow_high_risk_mode=True
    )
    validator = RiskProfileValidator()
    result = validator.validate(profile, {})
    assert result.is_valid is True
    assert len(result.warnings) > 0

def test_exposure_validator_pass(profile):
    validator = ExposureValidator()
    # 500 max risk
    # 300 current, 100 new = 400
    context = {'current_open_risk_fiat': Decimal("300.0"), 'new_risk_fiat': Decimal("100.0")}
    result = validator.validate(profile, context)
    assert result.is_valid is True

def test_exposure_validator_fail(profile):
    validator = ExposureValidator()
    # 500 max risk
    # 450 current, 100 new = 550
    context = {'current_open_risk_fiat': Decimal("450.0"), 'new_risk_fiat': Decimal("100.0")}
    result = validator.validate(profile, context)
    assert result.is_valid is False
    assert "Exposure limit breached" in result.reason

def test_daily_loss_validator_pass(profile):
    validator = DailyLossValidator()
    # 300 max loss
    context = {'daily_loss_fiat': Decimal("250.0")}
    result = validator.validate(profile, context)
    assert result.is_valid is True

def test_daily_loss_validator_fail(profile):
    validator = DailyLossValidator()
    # 300 max loss
    context = {'daily_loss_fiat': Decimal("350.0")}
    result = validator.validate(profile, context)
    assert result.is_valid is False
    assert "Daily drawdown limit reached" in result.reason
