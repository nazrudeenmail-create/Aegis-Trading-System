from app.market_analysis.models import MarketRegime
from app.strategy.models.ranking import StrategyProfile

def get_ema_pullback_profile() -> StrategyProfile:
    return StrategyProfile(
        name="EMA Trend Pullback",
        preferred_regimes=[MarketRegime.TRENDING],
        acceptable_regimes=[MarketRegime.BREAKOUT],
        avoided_regimes=[MarketRegime.RANGING],
        preferred_timeframes=["15M", "1H"],
        minimum_adx=25.0,
        volatility_preference="Normal to High",
        preferred_direction=None,  # Neutral
        max_atr_expansion=2.5
    )
