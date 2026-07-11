from app.market_analysis.tier2_base import BaseTier2Analyzer
from app.market_analysis.models import MomentumAnalysis, MarketSnapshot

class MomentumAnalyzer(BaseTier2Analyzer[MomentumAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> MomentumAnalysis:
        # Placeholder until RSI/MACD
        return MomentumAnalysis(momentum=None)
