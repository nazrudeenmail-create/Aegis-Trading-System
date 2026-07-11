from enum import Enum

class TrendDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    RANGING = "ranging"

class TrendStrength(str, Enum):
    STRONG = "strong"
    WEAK = "weak"
    NONE = "none"

class EMAAlignment(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    MIXED = "mixed"

class MarketRegime(str, Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    BREAKOUT = "breakout"
    CAPITULATION = "capitulation"

class VolatilityState(str, Enum):
    EXPANDING = "expanding"
    CONTRACTING = "contracting"
    NORMAL = "normal"

class MomentumState(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
