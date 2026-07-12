from typing import List, Dict, Any
from app.market.domain.candle import Candle
from app.market_analysis.mtf_service import MultiTimeframeService
from app.strategy.models import TradeCandidate, StrategyResult
from app.strategy.base import BaseStrategy

# Import all strategies
from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
from app.strategy.strategies.mtf_trend_alignment import MultiTimeframeTrendAlignmentStrategy
from app.strategy.strategies.donchian_breakout import DonchianChannelBreakoutStrategy

class StrategyEngine:
    """
    Orchestrates the evaluation of all registered trading strategies.
    Uses MultiTimeframeService to prepare contexts for each strategy.
    """
    
    def __init__(self, mtf_service: MultiTimeframeService = None):
        self.mtf_service = mtf_service or MultiTimeframeService()
        self.strategies: List[BaseStrategy] = [
            EMATrendPullbackStrategy(),
            MultiTimeframeTrendAlignmentStrategy(),
            DonchianChannelBreakoutStrategy()
        ]
        
    def evaluate_all(self, base_1m_candles: List[Candle]) -> List[TradeCandidate]:
        """
        Evaluates the base candles against all registered strategies.
        Returns a list of valid TradeCandidates.
        """
        results: Dict[str, StrategyResult] = {}
        valid_candidates: List[TradeCandidate] = []
        
        for strategy in self.strategies:
            # Build the specific context required by the strategy
            context = self.mtf_service.build_context(
                base_1m_candles=base_1m_candles,
                required_timeframes=strategy.required_timeframes,
                primary_timeframe=strategy.primary_timeframe
            )
            
            result = strategy.evaluate(context)
            results[strategy.name] = result
            
            if result.is_valid and result.candidate:
                valid_candidates.append(result.candidate)
            
        return valid_candidates
