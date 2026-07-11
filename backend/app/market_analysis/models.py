from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Optional
from app.market.domain.candle import Candle

class BaseAnalysis(BaseModel):
    """
    Base class for all analyzer results.
    Every specific analyzer result (e.g. EMAAnalysis, ATRAnalysis) 
    must inherit from this.
    """
    pass

class EMAAnalysis(BaseAnalysis):
    """
    Typed result for the EMA Analyzer.
    All decimal outputs from Pandas-TA must be converted to float/Decimal before reaching this model.
    """
    ema_9: Decimal | None
    ema_20: Decimal | None
    ema_21: Decimal | None
    ema_50: Decimal | None
    ema_100: Decimal | None
    ema_200: Decimal | None

class ATRAnalysis(BaseAnalysis):
    """Typed result for the ATR Analyzer."""
    atr: Decimal | None

class ADXAnalysis(BaseAnalysis):
    """Typed result for the ADX Analyzer."""
    adx: Decimal | None
    dmp: Decimal | None # +DI
    dmn: Decimal | None # -DI

class VolumeAnalysis(BaseAnalysis):
    """Typed result for the Volume Analyzer."""
    current_volume: Decimal | None
    average_volume: Decimal | None

class CandleAnalysis(BaseAnalysis):
    """Typed result for the Candle Analyzer."""
    is_bullish: bool
    is_bearish: bool
    is_engulfing: bool
    is_inside_bar: bool
    is_rejection: bool

class SwingAnalysis(BaseAnalysis):
    """Typed result for the Swing Analyzer."""
    swing_high: Decimal | None
    swing_low: Decimal | None

from app.market_analysis.enums import (
    TrendDirection, TrendStrength, EMAAlignment,
    MarketRegime, VolatilityState, MomentumState
)

# --- Tier 2 Models (Intelligence / Interpretation) ---

class EMAAlignmentAnalysis(BaseAnalysis):
    """Tier 2: Evaluates the relationship between EMAs."""
    timeframe: str
    alignment: EMAAlignment
    stack: List[str]
    strength: TrendStrength


class TrendAnalysis(BaseAnalysis):
    """Tier 2: Interprets trend direction and strength based on EMAs and ADX."""
    direction: TrendDirection
    strength: TrendStrength
    ema_alignment: EMAAlignment

class MarketRegimeAnalysis(BaseAnalysis):
    """Tier 2: Classifies the broader market regime based on Trend, Volatility, and Volume."""
    regime: MarketRegime | None
    is_tradable: bool = False

class MomentumAnalysis(BaseAnalysis):
    """Tier 2: Basic momentum interpretation (placeholder until RSI/MACD are added)."""
    momentum: MomentumState | None

class PullbackAnalysis(BaseAnalysis):
    """Tier 2: Detects if price is currently in a valid pullback to key MAs."""
    is_pullback: bool
    distance_from_ema20: Decimal | None
    target_ma: str | None # e.g., 'ema_20', 'ema_50'

class VolatilityAnalysis(BaseAnalysis):
    """Tier 2: Interprets current volatility relative to historical."""
    state: VolatilityState | None

from datetime import datetime, timezone

class MarketSnapshot(BaseModel):
    """
    The unified market intelligence snapshot produced by the MarketAnalysisService.
    Contains strictly typed fields for every analyzer output, plus the raw candles.
    """
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_errors: List[str] = Field(default_factory=list)
    
    # Raw Data
    candles: List[Candle] = Field(default_factory=list)
    
    # Tier 1 Facts
    ema: EMAAnalysis | None = None
    atr: ATRAnalysis | None = None
    adx: ADXAnalysis | None = None
    volume: VolumeAnalysis | None = None
    candle: CandleAnalysis | None = None
    swing: SwingAnalysis | None = None
    
    # Tier 2 Intelligence
    ema_alignment: EMAAlignmentAnalysis | None = None
    trend: TrendAnalysis | None = None
    regime: MarketRegimeAnalysis | None = None
    momentum: MomentumAnalysis | None = None
    pullback: PullbackAnalysis | None = None
    volatility: VolatilityAnalysis | None = None
    
    @property
    def is_valid(self) -> bool:
        return len(self.candles) > 0
