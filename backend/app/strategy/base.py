from abc import ABC, abstractmethod
from typing import List

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext
from app.strategy.models import StrategyResult

class BaseStrategy(ABC):
    """
    Abstract base class for all Trading Strategies.
    """
    name: str
    version: str
    description: str
    
    # The timeframe upon which the actual entry signal is based
    primary_timeframe: Timeframe
    
    # All timeframes required by this strategy (ordered highest to lowest)
    required_timeframes: List[Timeframe]

    @abstractmethod
    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        """
        Evaluates a MultiTimeframeContext against the strategy's rules.
        Returns a StrategyResult containing either a TradeCandidate or a rejection reason.
        """
        pass
