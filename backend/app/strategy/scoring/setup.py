from app.strategy.models import StrategyResult
from app.strategy.models.ranking import SetupScore

class SetupScorer:
    """
    Computes the Setup Score based on the StrategyResult.
    """
    @staticmethod
    def score(strategy_name: str, result: StrategyResult) -> SetupScore:
        failed_rule_dict = result.failed_rule.model_dump() if getattr(result, 'failed_rule', None) else None
        
        if not result.is_valid or not result.candidate:
            return SetupScore(
                strategy_name=strategy_name,
                has_setup=False,
                confidence=0.0,
                rejection_reason=result.rejection_reason or "No candidate generated",
                setup_progress=result.setup_progress,
                failed_rule=failed_rule_dict
            )
            
        conf = getattr(result.candidate, 'confidence', 100.0)
        
        return SetupScore(
            strategy_name=strategy_name,
            has_setup=True,
            confidence=float(conf),
            rejection_reason=None,
            setup_progress=100.0,
            failed_rule=None
        )
