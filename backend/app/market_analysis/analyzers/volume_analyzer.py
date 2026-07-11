from typing import List
from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import VolumeAnalysis, MarketSnapshot
from app.market_analysis.indicators.volume import calculate_volume_sma

class VolumeAnalyzer(BaseAnalyzer[VolumeAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> VolumeAnalysis:
        results = calculate_volume_sma(snapshot.candles, length=20)
        curr = results["current"]
        avg = results["average"]
        
        return VolumeAnalysis(
            current_volume=curr,
            average_volume=avg
        )
