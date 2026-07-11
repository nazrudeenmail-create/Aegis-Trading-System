from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import EMAAnalysis, MarketSnapshot
from app.market_analysis.indicators.ema import calculate_emas

class EMAAnalyzer(BaseAnalyzer[EMAAnalysis]):
    """
    Tier 1 Analyzer: Exponential Moving Average
    Calculates EMAs and determines their alignment.
    """
    
    def analyze(self, snapshot: MarketSnapshot) -> EMAAnalysis:
        # 1. Call the mathematical indicator wrapper
        # We need the 6 EMAs defined in our requirements
        lengths = [9, 20, 21, 50, 100, 200]
        results = calculate_emas(snapshot.candles, lengths)
        
        # 2. Extract values safely
        ema_9 = results.get(9)
        ema_20 = results.get(20)
        ema_21 = results.get(21)
        ema_50 = results.get(50)
        ema_100 = results.get(100)
        ema_200 = results.get(200)
        
        # 3. Return the strictly typed Pydantic model (Facts only)
        return EMAAnalysis(
            ema_9=ema_9,
            ema_20=ema_20,
            ema_21=ema_21,
            ema_50=ema_50,
            ema_100=ema_100,
            ema_200=ema_200
        )
