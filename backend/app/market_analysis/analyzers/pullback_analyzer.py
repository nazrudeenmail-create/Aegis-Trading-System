from app.market_analysis.tier2_base import BaseTier2Analyzer
from app.market_analysis.models import PullbackAnalysis, MarketSnapshot
from app.market_analysis.enums import TrendDirection
from decimal import Decimal

class PullbackAnalyzer(BaseTier2Analyzer[PullbackAnalysis]):
    def analyze(self, snapshot: MarketSnapshot) -> PullbackAnalysis:
        is_pullback = False
        target_ma = None
        distance_from_ema20 = None
        
        if not snapshot.trend or not snapshot.ema or not snapshot.candles:
            return PullbackAnalysis(is_pullback=False, distance_from_ema20=None, target_ma=None)
            
        trend_dir = snapshot.trend.direction
        last_candle = snapshot.candles[-1]
        close = last_candle.close
        
        ema_20 = snapshot.ema.ema_20
        ema_50 = snapshot.ema.ema_50
        
        if ema_20 and ema_50:
            if trend_dir == TrendDirection.BULLISH and close < ema_20 and close > ema_50:
                if snapshot.atr and snapshot.atr.atr:
                    distance = abs(close - ema_20)
                    distance_from_ema20 = distance
                    max_dist = Decimal("0.2") * snapshot.atr.atr
                    if distance <= max_dist:
                        is_pullback = True
                        target_ma = "ema_50"
                        
            elif trend_dir == TrendDirection.BEARISH and close > ema_20 and close < ema_50:
                if snapshot.atr and snapshot.atr.atr:
                    distance = abs(close - ema_20)
                    distance_from_ema20 = distance
                    max_dist = Decimal("0.2") * snapshot.atr.atr
                    if distance <= max_dist:
                        is_pullback = True
                        target_ma = "ema_50"
                
        return PullbackAnalysis(
            is_pullback=is_pullback,
            distance_from_ema20=distance_from_ema20,
            target_ma=target_ma
        )
