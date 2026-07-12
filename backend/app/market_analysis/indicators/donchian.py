import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional
from decimal import Decimal
import numpy as np

def calculate_donchian_channel(df: pd.DataFrame, period: int = 20) -> Dict[str, Optional[Decimal]]:
    """
    Calculates the Donchian Channel using pandas-ta.
    Returns the upper, lower, and middle bands for the most recent candle.
    """
    if len(df) < period:
        return {
            "upper_band": None,
            "lower_band": None,
            "middle_band": None
        }

    # pandas-ta returns DCL_20_20, DCM_20_20, DCU_20_20 (Lower, Middle, Upper)
    # The default for donchian is lower_length=period, upper_length=period
    donchian = ta.donchian(high=df['high'], low=df['low'], lower_length=period, upper_length=period)
    
    if donchian is None or donchian.empty:
        return {
            "upper_band": None,
            "lower_band": None,
            "middle_band": None
        }

    last_row = donchian.iloc[-1]
    
    lower_col = f"DCL_{period}_{period}"
    mid_col = f"DCM_{period}_{period}"
    upper_col = f"DCU_{period}_{period}"

    def safe_decimal(val) -> Optional[Decimal]:
        if pd.isna(val):
            return None
        return Decimal(str(val))

    return {
        "lower_band": safe_decimal(last_row.get(lower_col)),
        "middle_band": safe_decimal(last_row.get(mid_col)),
        "upper_band": safe_decimal(last_row.get(upper_col))
    }
