from app.market.domain.timeframe import Timeframe
import pytest
from app.market_analysis.service import MarketAnalysisService
from app.market.domain.candle import Candle
from datetime import datetime
from decimal import Decimal

def generate_candles(count: int, base_price: float = 100.0, trend: float = 0.1) -> list[Candle]:
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

def test_service_orchestration():
    service = MarketAnalysisService()
    candles = generate_candles(210, trend=1.0)
    
    snapshot = service.analyze(candles)
    
    # Check that snapshot is fully populated
    assert snapshot.is_valid is True
    assert len(snapshot.analysis_errors) == 0
    
    # Tier 1 checks
    assert snapshot.ema is not None
    assert snapshot.ema.ema_200 is not None
    assert snapshot.atr is not None
    assert snapshot.adx is not None
    assert snapshot.volume is not None
    
    # Tier 2 checks
    assert snapshot.trend is not None
    assert snapshot.trend.direction.value == "bullish"
    assert snapshot.trend.strength.value == "strong"
    
    assert snapshot.pullback is not None
    assert snapshot.regime is not None
    
def test_service_empty_candles():
    service = MarketAnalysisService()
    snapshot = service.analyze([])
    
    assert snapshot.is_valid is False
    assert snapshot.ema is None
    assert snapshot.trend is None
