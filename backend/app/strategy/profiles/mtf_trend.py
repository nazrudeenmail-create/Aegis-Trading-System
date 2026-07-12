from app.market_analysis.models import MarketRegime
from app.strategy.models.ranking import StrategyProfile

def get_mtf_trend_profile() -> StrategyProfile:
    return StrategyProfile(
        name="MTF Trend Alignment",
        preferred_regimes=[MarketRegime.TRENDING],
        acceptable_regimes=[],
        avoided_regimes=[MarketRegime.RANGING, MarketRegime.BREAKOUT],
        preferred_timeframes=["1H", "4H", "1D"],
        minimum_adx=25.0,
        volatility_preference="Normal",
        preferred_direction=None,
        max_atr_expansion=2.0
    )
