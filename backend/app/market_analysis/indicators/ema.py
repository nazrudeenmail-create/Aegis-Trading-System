import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Optional
from decimal import Decimal
from app.market.domain.candle import Candle
from app.market_analysis.exceptions import IndicatorCalculationError

def calculate_emas(candles: List[Candle], lengths: List[int]) -> Dict[int, Optional[Decimal]]:
    """
    Calculates multiple EMAs using pandas-ta.
    Returns a dictionary mapping EMA length to its latest value as a Decimal.
    """
    if not candles:
        return {length: None for length in lengths}
        
    df = pd.DataFrame([{"close": float(c.close)} for c in candles])
    
    results = {}
    for length in lengths:
        if len(df) < length:
            results[length] = None
            continue
            
        try:
            ema_series = ta.ema(df["close"], length=length)
            
            if ema_series is not None and not ema_series.empty and pd.notna(ema_series.iloc[-1]):
                results[length] = Decimal(str(ema_series.iloc[-1]))
            else:
                results[length] = None
        except Exception as e:
            raise IndicatorCalculationError(f"EMA {length} calculation failed: {e}")
            
    return results
