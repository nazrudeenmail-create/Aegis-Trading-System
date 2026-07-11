import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Optional
from decimal import Decimal
from app.market.domain.candle import Candle
from app.market_analysis.exceptions import IndicatorCalculationError

def calculate_adx(candles: List[Candle], length: int = 14) -> Dict[str, Optional[Decimal]]:
    """Calculates ADX using pandas-ta."""
    if len(candles) <= length:
        return {"adx": None, "dmp": None, "dmn": None}
        
    df = pd.DataFrame([{
        "high": float(c.high),
        "low": float(c.low),
        "close": float(c.close)
    } for c in candles])
    
    try:
        adx_df = ta.adx(df["high"], df["low"], df["close"], length=length)
        if adx_df is not None and not adx_df.empty:
            adx_col = f"ADX_{length}"
            dmp_col = f"DMP_{length}"
            dmn_col = f"DMN_{length}"
            
            last_row = adx_df.iloc[-1]
            return {
                "adx": Decimal(str(last_row[adx_col])) if pd.notna(last_row[adx_col]) else None,
                "dmp": Decimal(str(last_row[dmp_col])) if pd.notna(last_row[dmp_col]) else None,
                "dmn": Decimal(str(last_row[dmn_col])) if pd.notna(last_row[dmn_col]) else None,
            }
        return {"adx": None, "dmp": None, "dmn": None}
    except Exception as e:
        raise IndicatorCalculationError(f"ADX calculation failed: {e}")
