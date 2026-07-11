from app.market_analysis.tier2_base import BaseTier2Analyzer
from app.market_analysis.models import TrendAnalysis, MarketSnapshot
from app.market_analysis.enums import TrendDirection, TrendStrength, EMAAlignment

class TrendAnalyzer(BaseTier2Analyzer[TrendAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> TrendAnalysis:
        if not snapshot.ema:
            return TrendAnalysis(direction=TrendDirection.RANGING, strength=TrendStrength.NONE, ema_alignment=EMAAlignment.MIXED)
            
        ema_9 = snapshot.ema.ema_9
        ema_20 = snapshot.ema.ema_20
        ema_50 = snapshot.ema.ema_50
        ema_200 = snapshot.ema.ema_200
        
        alignment = EMAAlignment.MIXED
        direction = TrendDirection.RANGING
        
        if ema_9 and ema_20 and ema_50 and ema_200:
            if ema_9 > ema_20 > ema_50 > ema_200:
                alignment = EMAAlignment.BULLISH
                direction = TrendDirection.BULLISH
            elif ema_9 < ema_20 < ema_50 < ema_200:
                alignment = EMAAlignment.BEARISH
                direction = TrendDirection.BEARISH
                
        strength = TrendStrength.WEAK
        if snapshot.adx and snapshot.adx.adx:
            if snapshot.adx.adx >= 25:
                strength = TrendStrength.STRONG
                
        return TrendAnalysis(
            direction=direction,
            strength=strength,
            ema_alignment=alignment
        )
