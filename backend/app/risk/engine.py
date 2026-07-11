from typing import Dict, List
from decimal import Decimal

from app.strategy.models import TradeCandidate
from app.risk.models import RiskProfile, RiskAssessment
from app.risk.calculator import PositionCalculator
from app.risk.validator import RiskProfileValidator, ExposureValidator, DailyLossValidator

class RiskEngine:
    """
    Evaluates TradeCandidates against capital exposure rules.
    """
    def __init__(self):
        self.validators = [
            RiskProfileValidator(),
            ExposureValidator(),
            DailyLossValidator()
        ]
        self.calculator = PositionCalculator()

    def evaluate(self, candidate: TradeCandidate, profile: RiskProfile, context: Dict) -> RiskAssessment:
        """
        Evaluates a candidate and calculates its position size.
        Context should include:
        - current_open_risk_fiat: Decimal
        - daily_loss_fiat: Decimal
        """
        warnings = []
        
        # 1. Calculate ideal position size
        position_size, risk_amount, approved_risk_percent = self.calculator.calculate_position(candidate, profile)
        
        if position_size <= Decimal("0"):
            return RiskAssessment(
                is_approved=False,
                rejection_reason="Calculated position size is zero or invalid.",
                candidate=candidate
            )
            
        # 2. Update context for validators
        eval_context = dict(context)
        eval_context['new_risk_fiat'] = risk_amount
        
        # 3. Run all validators
        for validator in self.validators:
            result = validator.validate(profile, eval_context)
            if result.warnings:
                warnings.extend(result.warnings)
                
            if not result.is_valid:
                return RiskAssessment(
                    is_approved=False,
                    rejection_reason=result.reason,
                    warnings=warnings,
                    position_size=Decimal("0.0"),
                    risk_amount_fiat=Decimal("0.0"),
                    approved_risk_percent=Decimal("0.0"),
                    candidate=candidate
                )
                
        # 4. Success
        return RiskAssessment(
            is_approved=True,
            warnings=warnings,
            position_size=position_size,
            risk_amount_fiat=risk_amount,
            approved_risk_percent=approved_risk_percent,
            candidate=candidate
        )
