import pandas as pd
from typing import List, Dict, Optional
from decimal import Decimal
from app.market.domain.candle import Candle
from app.market_analysis.exceptions import IndicatorCalculationError

def detect_swings(candles: List[Candle], lookback: int = 5) -> Dict[str, Optional[Decimal]]:
    """
    Naive mathematical swing detection based on local highs/lows.
    Looks for a point that is the highest/lowest within a window.
    """
    if len(candles) < lookback * 2 + 1:
        return {"swing_high": None, "swing_low": None}
        
    df = pd.DataFrame([{
        "high": float(c.high),
        "low": float(c.low)
    } for c in candles])
    
    window = lookback * 2 + 1
    
    try:
        # Use pandas rolling max/min
        df['rolling_max'] = df['high'].rolling(window=window, center=True).max()
        df['rolling_min'] = df['low'].rolling(window=window, center=True).min()
        
        # Find points where high == rolling_max
        df['is_swing_high'] = (df['high'] == df['rolling_max'])
        df['is_swing_low'] = (df['low'] == df['rolling_min'])
        
        swing_highs = df[df['is_swing_high']]
        swing_lows = df[df['is_swing_low']]
        
        last_high = Decimal(str(swing_highs.iloc[-1]['high'])) if not swing_highs.empty else None
        last_low = Decimal(str(swing_lows.iloc[-1]['low'])) if not swing_lows.empty else None
        
        return {"swing_high": last_high, "swing_low": last_low}
    except Exception as e:
        raise IndicatorCalculationError(f"Swing detection failed: {e}")
