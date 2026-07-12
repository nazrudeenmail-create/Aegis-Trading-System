from app.strategy.models import StrategyResult
from app.strategy.models.ranking import SetupScore

class SetupScorer:
    """
    Computes the Setup Score based on the StrategyResult.
    """
    @staticmethod
    def score(strategy_name: str, result: StrategyResult) -> SetupScore:
        if not result.is_valid or not result.candidate:
            return SetupScore(
                strategy_name=strategy_name,
                has_setup=False,
                confidence=0.0,
                rejection_reason=result.rejection_reason or "No candidate generated"
            )
            
        # Assuming we eventually add confidence to TradeCandidate, 
        # or we just assume 100.0 for a valid setup for now.
        # If confidence is added to TradeCandidate, extract it: getattr(result.candidate, 'confidence', 100.0)
        conf = getattr(result.candidate, 'confidence', 100.0)
        
        return SetupScore(
            strategy_name=strategy_name,
            has_setup=True,
            confidence=float(conf),
            rejection_reason=None
        )
