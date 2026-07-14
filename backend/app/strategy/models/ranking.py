from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.market_analysis.models import MarketRegime

class StrategyProfile(BaseModel):
    name: str
    preferred_regimes: List[MarketRegime]
    acceptable_regimes: List[MarketRegime]
    avoided_regimes: List[MarketRegime]
    preferred_timeframes: List[str]
    minimum_adx: Optional[float] = None
    volatility_preference: str
    preferred_direction: Optional[str] = None
    max_atr_expansion: Optional[float] = None

class SetupScore(BaseModel):
    strategy_name: str
    has_setup: bool
    confidence: float
    rejection_reason: Optional[str] = None
    setup_progress: float = 0.0
    failed_rule: Optional[dict] = None

class StrategyScore(BaseModel):
    strategy_name: str
    historical_score: float
    market_score: float
    setup_score: float
    final_score: float
    rejection_reason: Optional[str] = None
    setup_progress: float = 0.0
    failed_rule: Optional[dict] = None

class RankingResult(BaseModel):
    timestamp: datetime
    symbol: str
    timeframe: str
    market_regime: Optional[MarketRegime] = None
    rankings: List[StrategyScore]
    selected_strategy: Optional[str] = None
    selection_reason: str
