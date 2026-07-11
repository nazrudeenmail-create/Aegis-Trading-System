from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from .models import BaseAnalysis, MarketSnapshot

# T is bound to BaseAnalysis, meaning any type T must be a subclass of BaseAnalysis
T = TypeVar('T', bound=BaseAnalysis)

class BaseAnalyzer(ABC, Generic[T]):
    """
    Abstract base class for all Market Analyzers (Tier 1 & Tier 2).
    
    Enforces that every analyzer must consume a MarketSnapshot
    and return a strongly-typed Pydantic model inheriting from BaseAnalysis.
    """
    
    @abstractmethod
    def analyze(self, snapshot: MarketSnapshot) -> T:
        """
        Analyze the provided snapshot and return the specific analysis model.
        """
        pass
