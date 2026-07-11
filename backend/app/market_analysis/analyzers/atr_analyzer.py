from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import ATRAnalysis, MarketSnapshot
from app.market_analysis.indicators.atr import calculate_atr

class ATRAnalyzer(BaseAnalyzer[ATRAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> ATRAnalysis:
        atr_value = calculate_atr(snapshot.candles, length=14)
        return ATRAnalysis(atr=atr_value)
