from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import CandleAnalysis, MarketSnapshot
from app.market_analysis.indicators.candle import analyze_last_candle

class CandleAnalyzer(BaseAnalyzer[CandleAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> CandleAnalysis:
        res = analyze_last_candle(snapshot.candles)
        # Ensure all fields are present
        if 'is_inside_bar' not in res:
            res['is_inside_bar'] = False
        return CandleAnalysis(**res)
