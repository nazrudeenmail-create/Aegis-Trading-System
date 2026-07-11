from decimal import Decimal
from typing import Tuple

from app.strategy.models import TradeCandidate
from app.risk.models import RiskProfile

class PositionCalculator:
    """
    Pure mathematics class for calculating position sizes based on a risk profile.
    It does not validate exposure limits.
    """

    @staticmethod
    def calculate_position(candidate: TradeCandidate, profile: RiskProfile) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculates position size and risk metrics.
        Returns: (position_size, risk_amount_fiat, approved_risk_percent)
        """
        if candidate.entry_price == candidate.stop_loss:
            return Decimal("0"), Decimal("0"), Decimal("0")

        # 1. Calculate how much fiat we are willing to risk
        risk_amount_fiat = profile.account_balance * (profile.risk_per_trade_percent / Decimal("100"))
        
        # 2. Calculate the distance from entry to stop loss
        stop_loss_distance = abs(candidate.entry_price - candidate.stop_loss)
            
        # 3. Calculate exactly how many shares/units we can buy
        position_size = risk_amount_fiat / stop_loss_distance
        
        # In a real broker, we might round down to nearest lot size, but for theoretical risk calculation
        # we return the exact mathematical size.
        return position_size, risk_amount_fiat, profile.risk_per_trade_percent
