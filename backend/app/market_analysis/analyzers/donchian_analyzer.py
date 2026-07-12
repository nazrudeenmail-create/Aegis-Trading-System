from decimal import Decimal
import pandas as pd
from typing import List

from app.market_analysis.base import BaseAnalyzer
from app.market_analysis.models import DonchianAnalysis, MarketSnapshot
from app.market_analysis.indicators.donchian import calculate_donchian_channel

class DonchianAnalyzer(BaseAnalyzer[DonchianAnalysis]):
    """
    Tier 1 Analyzer for Donchian Channel.
    Calculates channel boundaries and detects breakout conditions.
    """
    def __init__(self, period: int = 20):
        self.period = period

    def analyze(self, snapshot: MarketSnapshot) -> DonchianAnalysis:
        candles = snapshot.candles
        if not candles or len(candles) < self.period:
            return DonchianAnalysis(
                upper_band=None,
                lower_band=None,
                middle_band=None,
                channel_width=None,
                is_breakout_up=False,
                is_breakout_down=False
            )
            
        data = []
        for c in candles:
            data.append({
                "timestamp": c.timestamp,
                "open": float(c.open),
                "high": float(c.high),
                "low": float(c.low),
                "close": float(c.close),
                "volume": float(c.volume)
            })
        df = pd.DataFrame(data)
        
        # Calculate Donchian values
        donchian_data = calculate_donchian_channel(df, period=self.period)
        
        upper = donchian_data["upper_band"]
        lower = donchian_data["lower_band"]
        middle = donchian_data["middle_band"]
        
        if upper is None or lower is None:
            return DonchianAnalysis(
                upper_band=None,
                lower_band=None,
                middle_band=None,
                channel_width=None,
                is_breakout_up=False,
                is_breakout_down=False
            )
            
        channel_width = upper - lower
        
        last_candle = candles[-1]
        
        # Determine breakouts. We use close > upper for up, close < lower for down.
        # But remember, upper band includes the current candle's high by default in pandas-ta.
        # So a breakout means closing *above* previous period's upper_band.
        
        prev_df = df.iloc[:-1]
        prev_donchian_data = calculate_donchian_channel(prev_df, period=self.period)
        prev_upper = prev_donchian_data["upper_band"]
        prev_lower = prev_donchian_data["lower_band"]
        
        is_breakout_up = False
        is_breakout_down = False
        
        if prev_upper is not None and last_candle.close > prev_upper:
            is_breakout_up = True
            
        if prev_lower is not None and last_candle.close < prev_lower:
            is_breakout_down = True

        return DonchianAnalysis(
            upper_band=upper,
            lower_band=lower,
            middle_band=middle,
            channel_width=channel_width,
            is_breakout_up=is_breakout_up,
            is_breakout_down=is_breakout_down
        )
