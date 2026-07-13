from app.market.domain.timeframe import Timeframe
import pytest
from datetime import datetime
from decimal import Decimal
from typing import List

from app.market.domain.candle import Candle
from app.market_analysis.indicators.ema import calculate_emas
from app.market_analysis.indicators.atr import calculate_atr
from app.market_analysis.indicators.adx import calculate_adx
from app.market_analysis.indicators.candle import analyze_last_candle
from app.market_analysis.indicators.swing import detect_swings

def generate_candles(count: int, base_price: float = 100.0, trend: float = 0.1) -> List[Candle]:
    """Helper to generate a predictable series of candles."""
    candles = []
    current_price = base_price
    for i in range(count):
        close = current_price + trend
        candles.append(
            Candle(
                timestamp=datetime.utcnow(),
                instrument="BTC/USD",
                timeframe=Timeframe.M1,
                open=Decimal(str(current_price)),
                high=Decimal(str(max(current_price, close) + 1.0)),
                low=Decimal(str(min(current_price, close) - 1.0)),
                close=Decimal(str(close)),
                source="test", volume=Decimal("100.0")
            )
        )
        current_price = close
    return candles

def test_ema_calculation():
    # Need > 200 candles for EMA 200
    candles = generate_candles(210, trend=1.0)
    
    results = calculate_emas(candles, lengths=[9, 20, 50, 200])
    
    assert results[9] is not None
    assert results[20] is not None
    assert results[50] is not None
    assert results[200] is not None
    
    # In an uptrend, shorter EMA should be higher than longer EMA
    assert results[9] > results[20]
    assert results[20] > results[50]
    
    # Test insufficient data
    short_candles = generate_candles(15)
    short_results = calculate_emas(short_candles, lengths=[9, 20])
    assert short_results[9] is not None
    assert short_results[20] is None  # Not enough data for EMA 20

def test_atr_calculation():
    candles = generate_candles(50, trend=0.5)
    atr = calculate_atr(candles, length=14)
    assert atr is not None
    assert isinstance(atr, Decimal)
    assert atr > Decimal("0")

def test_adx_calculation():
    candles = generate_candles(50, trend=2.0)
    results = calculate_adx(candles, length=14)
    
    assert results["adx"] is not None
    assert results["dmp"] is not None
    assert results["dmn"] is not None
    assert isinstance(results["adx"], Decimal)
    
    # Since we are in a strong uptrend, +DI should be greater than -DI
    assert results["dmp"] > results["dmn"]

def test_candle_analysis_bullish_engulfing():
    candles = [
        Candle(
            timestamp=datetime.utcnow(), instrument="BTC/USD", timeframe=Timeframe.M1, source="test",
            open=Decimal("100.0"), high=Decimal("101.0"), low=Decimal("99.0"), close=Decimal("99.5"), volume=Decimal("10")
        ), # Bearish candle
        Candle(
            timestamp=datetime.utcnow(), instrument="BTC/USD", timeframe=Timeframe.M1, source="test",
            open=Decimal("99.0"), high=Decimal("102.0"), low=Decimal("98.0"), close=Decimal("101.5"), volume=Decimal("20")
        ) # Bullish engulfing
    ]
    
    res = analyze_last_candle(candles)
    assert res["is_bullish"] is True
    assert res["is_bearish"] is False
    assert res["is_engulfing"] is True
    
def test_swing_detection():
    # Generate a peak
    candles = []
    prices = [100, 102, 105, 103, 101]
    for p in prices:
        candles.append(Candle(
            timestamp=datetime.utcnow(), instrument="BTC/USD", timeframe=Timeframe.M1, source="test",
            open=Decimal(str(p)), high=Decimal(str(p)), low=Decimal(str(p)), close=Decimal(str(p)), volume=Decimal("10")
        ))
        
    # lookback=2 means window=5
    results = detect_swings(candles, lookback=2)
    assert results["swing_high"] == Decimal("105")
