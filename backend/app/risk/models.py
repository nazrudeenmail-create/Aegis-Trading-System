from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from app.strategy.models import TradeCandidate

class RiskProfile(BaseModel):
    """
    User-configurable risk profile defining how much capital to expose.
    """
    account_balance: Decimal
    risk_per_trade_percent: Decimal = Field(default=Decimal("1.0"), ge=Decimal("0.0"))
    max_open_risk_percent: Decimal = Field(default=Decimal("5.0"), ge=Decimal("0.0"))
    max_daily_drawdown_percent: Decimal = Field(default=Decimal("3.0"), ge=Decimal("0.0"))
    allow_high_risk_mode: bool = False

class RiskAssessment(BaseModel):
    """
    The output of the Risk Management Engine for a single TradeCandidate.
    """
    is_approved: bool
    rejection_reason: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    position_size: Decimal = Decimal("0.0")
    risk_amount_fiat: Decimal = Decimal("0.0")
    approved_risk_percent: Decimal = Decimal("0.0")
    candidate: TradeCandidate
