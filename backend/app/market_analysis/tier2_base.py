from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from app.market_analysis.models import MarketSnapshot

T = TypeVar("T")

class BaseTier2Analyzer(Generic[T], ABC):
    """
    Abstract base class for Tier 2 Market Intelligence Analyzers.
    Enforces consumption of a MarketSnapshot.
    """
    @abstractmethod
    def analyze(self, snapshot: MarketSnapshot) -> T:
        pass
