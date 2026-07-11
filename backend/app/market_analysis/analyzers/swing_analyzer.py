from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import SwingAnalysis, MarketSnapshot
from app.market_analysis.indicators.swing import detect_swings

class SwingAnalyzer(BaseAnalyzer[SwingAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> SwingAnalysis:
        results = detect_swings(snapshot.candles, lookback=5)
        
        return SwingAnalysis(
            swing_high=results["swing_high"],
            swing_low=results["swing_low"]
        )
