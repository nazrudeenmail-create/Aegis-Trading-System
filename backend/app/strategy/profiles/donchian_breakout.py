from app.market_analysis.models import MarketRegime
from app.strategy.models.ranking import StrategyProfile

def get_donchian_breakout_profile() -> StrategyProfile:
    return StrategyProfile(
        name="Donchian Channel Breakout",
        preferred_regimes=[MarketRegime.TRENDING, MarketRegime.BREAKOUT],
        acceptable_regimes=[MarketRegime.RANGING], # Ranging breakouts can start new trends
        avoided_regimes=[],
        preferred_timeframes=["15M", "1H"],
        minimum_adx=20.0,
        volatility_preference="High",
        preferred_direction=None,
        max_atr_expansion=3.0
    )
