from app.market_analysis.tier2_base import BaseTier2Analyzer
from app.market_analysis.models import MarketRegimeAnalysis, MarketSnapshot
from app.market_analysis.enums import MarketRegime, TrendStrength, VolatilityState

class MarketRegimeAnalyzer(BaseTier2Analyzer[MarketRegimeAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> MarketRegimeAnalysis:
        regime = MarketRegime.RANGING
        is_tradable = True
        
        if snapshot.trend:
            if snapshot.trend.strength == TrendStrength.STRONG:
                regime = MarketRegime.TRENDING
            
        if snapshot.volatility and snapshot.volatility.state == VolatilityState.EXPANDING:
            is_tradable = False
            
        return MarketRegimeAnalysis(
            regime=regime,
            is_tradable=is_tradable
        )
