import pandas as pd
import pandas_ta as ta
from typing import List, Optional
from decimal import Decimal
from app.market.domain.candle import Candle
from app.market_analysis.exceptions import IndicatorCalculationError

def calculate_atr(candles: List[Candle], length: int = 14) -> Optional[Decimal]:
    """Calculates ATR using pandas-ta."""
    if len(candles) <= length:
        return None
        
    df = pd.DataFrame([{
        "high": float(c.high),
        "low": float(c.low),
        "close": float(c.close)
    } for c in candles])
    
    try:
        atr_series = ta.atr(df["high"], df["low"], df["close"], length=length)
        if atr_series is not None and not atr_series.empty and pd.notna(atr_series.iloc[-1]):
            return Decimal(str(atr_series.iloc[-1]))
        return None
    except Exception as e:
        raise IndicatorCalculationError(f"ATR calculation failed: {e}")
