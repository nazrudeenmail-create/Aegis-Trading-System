import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Optional
from decimal import Decimal
from app.market.domain.candle import Candle
from app.market_analysis.exceptions import IndicatorCalculationError

def calculate_volume_sma(candles: List[Candle], length: int = 20) -> Dict[str, Optional[Decimal]]:
    """Calculates a simple moving average of volume."""
    if not candles:
        return {"current": None, "average": None}
        
    df = pd.DataFrame([{"volume": float(c.volume)} for c in candles])
    current_vol = Decimal(str(df["volume"].iloc[-1]))
    
    if len(df) < length:
        return {"current": current_vol, "average": None}
        
    try:
        sma = ta.sma(df["volume"], length=length)
        avg_vol = Decimal(str(sma.iloc[-1])) if pd.notna(sma.iloc[-1]) else None
        
        return {"current": current_vol, "average": avg_vol}
    except Exception as e:
        raise IndicatorCalculationError(f"Volume SMA calculation failed: {e}")
