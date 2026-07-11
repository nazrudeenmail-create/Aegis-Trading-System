from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import CandleAnalysis, MarketSnapshot
from app.market_analysis.indicators.candle import analyze_last_candle

class CandleAnalyzer(BaseAnalyzer[CandleAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> CandleAnalysis:
        res = analyze_last_candle(snapshot.candles)
        return CandleAnalysis(**res)
