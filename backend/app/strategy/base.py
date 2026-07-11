from abc import ABC, abstractmethod
from app.market_analysis.models import MarketSnapshot
from app.strategy.models import StrategyResult

class BaseStrategy(ABC):
    """
    Abstract base class for all Trading Strategies.
    """
    name: str
    version: str
    description: str

    @abstractmethod
    def evaluate(self, snapshot: MarketSnapshot) -> StrategyResult:
        """
        Evaluates a MarketSnapshot against the strategy's rules.
        Returns a StrategyResult containing either a TradeCandidate or a rejection reason.
        """
        pass
