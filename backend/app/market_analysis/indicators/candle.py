from typing import List, Dict
from app.market.domain.candle import Candle

def analyze_last_candle(candles: List[Candle]) -> Dict[str, bool]:
    """Analyzes recent candle behavior (bullish, bearish, engulfing, rejection)."""
    if len(candles) < 2:
        return {"is_bullish": False, "is_bearish": False, "is_engulfing": False, "is_rejection": False}
        
    curr = candles[-1]
    prev = candles[-2]
    
    is_bullish = curr.close > curr.open
    is_bearish = curr.close < curr.open
    
    body = abs(float(curr.close) - float(curr.open))
    top_wick = float(curr.high) - max(float(curr.open), float(curr.close))
    bot_wick = min(float(curr.open), float(curr.close)) - float(curr.low)
    
    is_rejection = (top_wick > body * 2) or (bot_wick > body * 2)
    
    # Simple engulfing logic
    prev_body = abs(float(prev.close) - float(prev.open))
    is_engulfing = False
    
    if is_bullish and float(prev.close) < float(prev.open) and body > prev_body and float(curr.close) > float(prev.open) and float(curr.open) < float(prev.close):
        is_engulfing = True
    elif is_bearish and float(prev.close) > float(prev.open) and body > prev_body and float(curr.close) < float(prev.open) and float(curr.open) > float(prev.close):
        is_engulfing = True
        
    # Inside bar logic
    is_inside_bar = float(curr.high) <= float(prev.high) and float(curr.low) >= float(prev.low)
        
    return {
        "is_bullish": is_bullish,
        "is_bearish": is_bearish,
        "is_engulfing": is_engulfing,
        "is_rejection": is_rejection,
        "is_inside_bar": is_inside_bar
    }
