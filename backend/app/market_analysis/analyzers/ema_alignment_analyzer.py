from typing import Optional
from app.market_analysis.tier2_base import BaseTier2Analyzer
from app.market_analysis.models import MarketSnapshot, EMAAlignmentAnalysis
from app.market_analysis.enums import EMAAlignment, TrendStrength

class EMAAlignmentAnalyzer(BaseTier2Analyzer[EMAAlignmentAnalysis]):
    """
    Evaluates the relationship and alignment of EMAs.
    Requires Tier 1: EMAAnalysis
    """
    
    def analyze(self, snapshot: MarketSnapshot) -> EMAAlignmentAnalysis:
        timeframe = snapshot.candles[-1].timeframe if snapshot.candles else "UNKNOWN"

        if not snapshot.ema:
            return EMAAlignmentAnalysis(
                timeframe=timeframe,
                alignment=EMAAlignment.MIXED,
                stack=[],
                strength=TrendStrength.NONE
            )
            
        timeframe = snapshot.candles[-1].timeframe if snapshot.candles else "UNKNOWN"
        
        emas = {
            "EMA9": snapshot.ema.ema_9,
            "EMA20": snapshot.ema.ema_20,
            "EMA50": snapshot.ema.ema_50,
            "EMA100": snapshot.ema.ema_100,
            "EMA200": snapshot.ema.ema_200,
        }
        
        # Filter out None values
        valid_emas = {k: v for k, v in emas.items() if v is not None}
        
        if len(valid_emas) < 2:
            return EMAAlignmentAnalysis(
                timeframe=timeframe,
                alignment=EMAAlignment.MIXED,
                stack=list(valid_emas.keys()),
                strength=TrendStrength.NONE
            )
            
        sorted_emas = sorted(valid_emas.items(), key=lambda x: x[1], reverse=True)
        stack = [k for k, v in sorted_emas]
        
        # Determine alignment
        keys_ordered = ["EMA9", "EMA20", "EMA50", "EMA100", "EMA200"]
        present_keys = [k for k in keys_ordered if k in valid_emas]
        
        is_bullish = stack == present_keys
        is_bearish = stack == list(reversed(present_keys))
        
        alignment = EMAAlignment.MIXED
        strength = TrendStrength.NONE
        
        if is_bullish:
            alignment = EMAAlignment.BULLISH
            # Check strength based on distance, but for now we just mark it STRONG if fully aligned
            strength = TrendStrength.STRONG if len(valid_emas) >= 4 else TrendStrength.WEAK
        elif is_bearish:
            alignment = EMAAlignment.BEARISH
            strength = TrendStrength.STRONG if len(valid_emas) >= 4 else TrendStrength.WEAK
        else:
            # Check for partial alignment
            if valid_emas.get("EMA20") and valid_emas.get("EMA50"):
                if valid_emas["EMA20"] > valid_emas["EMA50"]:
                    strength = TrendStrength.WEAK
                elif valid_emas["EMA20"] < valid_emas["EMA50"]:
                    strength = TrendStrength.WEAK
        
        return EMAAlignmentAnalysis(
            timeframe=timeframe,
            alignment=alignment,
            stack=stack,
            strength=strength
        )
