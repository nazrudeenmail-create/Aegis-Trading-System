from typing import List, Tuple, Dict
from decimal import Decimal

from app.risk.models import RiskProfile

class ValidationResult:
    def __init__(self, is_valid: bool, reason: str = "", warnings: List[str] = None):
        self.is_valid = is_valid
        self.reason = reason
        self.warnings = warnings or []

class BaseValidator:
    def validate(self, profile: RiskProfile, context: Dict) -> ValidationResult:
        raise NotImplementedError

class RiskProfileValidator(BaseValidator):
    """
    Validates that the risk profile itself is sane.
    """
    def validate(self, profile: RiskProfile, context: Dict) -> ValidationResult:
        warnings = []
        if profile.max_open_risk_percent > Decimal("20.0"):
            warnings.append(f"High risk configuration detected. Maximum open risk: {profile.max_open_risk_percent}%")
            if not profile.allow_high_risk_mode:
                return ValidationResult(False, "Max open risk exceeds 20% but allow_high_risk_mode is False.", warnings)
        
        if profile.risk_per_trade_percent > Decimal("5.0"):
            warnings.append(f"Aggressive risk per trade: {profile.risk_per_trade_percent}%")
            if not profile.allow_high_risk_mode:
                return ValidationResult(False, "Risk per trade exceeds 5% but allow_high_risk_mode is False.", warnings)
                
        return ValidationResult(True, warnings=warnings)

class ExposureValidator(BaseValidator):
    """
    Validates that adding a new trade won't breach max open risk limits.
    Requires 'current_open_risk_fiat' and 'new_risk_fiat' in context.
    """
    def validate(self, profile: RiskProfile, context: Dict) -> ValidationResult:
        current_open_risk = context.get('current_open_risk_fiat', Decimal("0"))
        new_risk = context.get('new_risk_fiat', Decimal("0"))
        
        total_risk = current_open_risk + new_risk
        max_allowed_risk = profile.account_balance * (profile.max_open_risk_percent / Decimal("100"))
        
        if total_risk > max_allowed_risk:
            msg = f"Exposure limit breached. Total risk {total_risk} exceeds max {max_allowed_risk}"
            if profile.allow_high_risk_mode:
                return ValidationResult(True, warnings=[f"Bypassed exposure limit: {msg}"])
            return ValidationResult(False, msg)
            
        return ValidationResult(True)

class DailyLossValidator(BaseValidator):
    """
    Validates that daily losses haven't breached the max daily drawdown.
    Requires 'daily_loss_fiat' in context.
    """
    def validate(self, profile: RiskProfile, context: Dict) -> ValidationResult:
        daily_loss = context.get('daily_loss_fiat', Decimal("0"))
        
        # Loss should be positive number for this calculation
        if daily_loss <= Decimal("0"):
            return ValidationResult(True)
            
        max_allowed_loss = profile.account_balance * (profile.max_daily_drawdown_percent / Decimal("100"))
        
        if daily_loss >= max_allowed_loss:
            msg = f"Daily drawdown limit reached. Loss {daily_loss} exceeds max {max_allowed_loss}"
            if profile.allow_high_risk_mode:
                return ValidationResult(True, warnings=[f"Bypassed daily drawdown limit: {msg}"])
            return ValidationResult(False, msg)
            
        return ValidationResult(True)
