import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.risk.models import RiskProfile

def test_risk_profile_defaults():
    profile = RiskProfile(account_balance=Decimal("10000.0"))
    assert profile.account_balance == Decimal("10000.0")
    assert profile.risk_per_trade_percent == Decimal("1.0")
    assert profile.max_open_risk_percent == Decimal("5.0")
    assert profile.max_daily_drawdown_percent == Decimal("3.0")
    assert profile.allow_high_risk_mode is False

def test_risk_profile_validation():
    with pytest.raises(ValidationError):
        RiskProfile(account_balance=Decimal("10000.0"), risk_per_trade_percent=Decimal("-1.0"))
