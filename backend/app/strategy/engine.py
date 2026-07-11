from typing import List, Dict, Any
from app.market_analysis.models import MarketSnapshot
from app.strategy.models import TradeCandidate, StrategyResult
from app.strategy.base import BaseStrategy

# Import all strategies
from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy

class StrategyEngine:
    """
    Orchestrates the evaluation of all registered trading strategies.
    Receives market snapshots and returns a list of valid TradeCandidates.
    """
    
    def __init__(self):
        self.strategies: List[BaseStrategy] = [
            EMATrendPullbackStrategy()
            # Add future strategies here
        ]
        
    def evaluate_all(self, snapshot: MarketSnapshot) -> List[TradeCandidate]:
        """
        Evaluates the snapshot against all registered strategies.
        Returns a list of valid TradeCandidates.
        Internal rejection results are logged or can be retrieved if needed.
        """
        results: Dict[str, StrategyResult] = {}
        valid_candidates: List[TradeCandidate] = []
        
        for strategy in self.strategies:
            result = strategy.evaluate(snapshot)
            results[strategy.name] = result
            
            if result.is_valid and result.candidate:
                valid_candidates.append(result.candidate)
            # In the future, we could log `results` or store them for analysis
            
        return valid_candidates
