from typing import List, Tuple
from app.market.domain.candle import Candle

class DataQualityValidator:
    """
    Validates market data before indicator calculations to prevent 
    bad data from causing false signals.
    """
    @staticmethod
    def validate(candles: List[Candle], expected_count: int = 10) -> Tuple[bool, str]:
        if not candles:
            return False, "No candles provided"
            
        if len(candles) < expected_count:
            return False, f"Insufficient history. Required: {expected_count}, Available: {len(candles)}"
            
        # Check for gaps or invalid prices
        for i in range(len(candles)):
            c = candles[i]
            if c.high < c.low:
                return False, f"Invalid candle: High ({c.high}) < Low ({c.low}) at {c.timestamp}"
            if c.close < c.low or c.close > c.high:
                return False, f"Invalid candle: Close ({c.close}) outside High/Low range at {c.timestamp}"
            if c.open < c.low or c.open > c.high:
                return False, f"Invalid candle: Open ({c.open}) outside High/Low range at {c.timestamp}"
                
        # Additional checks can be added here (e.g. max time gap, volume anomalies)
        return True, "Data is valid"
