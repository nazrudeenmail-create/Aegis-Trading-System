from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import ADXAnalysis, MarketSnapshot
from app.market_analysis.indicators.adx import calculate_adx

class ADXAnalyzer(BaseAnalyzer[ADXAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> ADXAnalysis:
        results = calculate_adx(snapshot.candles, length=14)
        adx_val = results["adx"]
        
        return ADXAnalysis(
            adx=adx_val,
            dmp=results["dmp"],
            dmn=results["dmn"]
        )
