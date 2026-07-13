from app.market.domain.timeframe import Timeframe
import pytest
from decimal import Decimal

from app.market_analysis.models import (
    MarketSnapshot, EMAAnalysis, ADXAnalysis, ATRAnalysis, CandleAnalysis
)
from app.market_analysis.enums import TrendDirection, TrendStrength, EMAAlignment
from app.market_analysis.analyzers.trend_analyzer import TrendAnalyzer
from app.market_analysis.analyzers.pullback_analyzer import PullbackAnalyzer
from app.market.domain.candle import Candle
from datetime import datetime

@pytest.fixture
def base_snapshot():
    return MarketSnapshot()

def test_trend_analyzer_bullish():
    snapshot = MarketSnapshot()
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("100"),
        ema_20=Decimal("90"),
        ema_21=Decimal("89"),
        ema_50=Decimal("80"),
        ema_100=Decimal("70"),
        ema_200=Decimal("60")
    )
    snapshot.adx = ADXAnalysis(adx=Decimal("30"), dmp=Decimal("40"), dmn=Decimal("10"))
    
    analyzer = TrendAnalyzer()
    result = analyzer.analyze(snapshot)
    
    assert result.direction == TrendDirection.BULLISH
    assert result.strength == TrendStrength.STRONG
    assert result.ema_alignment == EMAAlignment.BULLISH

def test_trend_analyzer_ranging_without_data():
    snapshot = MarketSnapshot()
    analyzer = TrendAnalyzer()
    result = analyzer.analyze(snapshot)
    
    assert result.direction == TrendDirection.RANGING
    assert result.strength == TrendStrength.NONE
    assert result.ema_alignment == EMAAlignment.MIXED

def test_pullback_analyzer_optimal():
    snapshot = MarketSnapshot()
    
    # Mock a bullish trend
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("100"),
        ema_20=Decimal("90"),
        ema_21=Decimal("89"),
        ema_50=Decimal("80"),
        ema_100=Decimal("70"),
        ema_200=Decimal("60")
    )
    snapshot.adx = ADXAnalysis(adx=Decimal("30"), dmp=Decimal("40"), dmn=Decimal("10"))
    
    # Run trend analyzer to populate trend
    trend_analyzer = TrendAnalyzer()
    snapshot.trend = trend_analyzer.analyze(snapshot)
    
    # Mock ATR
    snapshot.atr = ATRAnalysis(atr=Decimal("10")) # 0.2 * 10 = 2.0 max distance
    
    # Mock a candle where close is just below EMA 20, within 0.2 ATR
    # EMA 20 = 90. Close = 89. Distance = 1. Max distance = 2.0.
    snapshot.candles = [
        Candle(
            timestamp=datetime.utcnow(), instrument="BTC/USD", timeframe=Timeframe.M1, source="test",
            open=Decimal("95"), high=Decimal("96"), low=Decimal("88"), close=Decimal("89"), volume=Decimal("100")
        )
    ]
    
    pullback_analyzer = PullbackAnalyzer()
    result = pullback_analyzer.analyze(snapshot)
    
    assert result.is_pullback is True
    assert result.target_ma == "ema_50"
    assert result.distance_from_ema20 == Decimal("1")

def test_pullback_analyzer_too_far():
    snapshot = MarketSnapshot()
    
    # Mock a bullish trend
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("100"),
        ema_20=Decimal("90"),
        ema_21=Decimal("89"),
        ema_50=Decimal("80"),
        ema_100=Decimal("70"),
        ema_200=Decimal("60")
    )
    
    trend_analyzer = TrendAnalyzer()
    snapshot.trend = trend_analyzer.analyze(snapshot)
    
    # Mock ATR
    snapshot.atr = ATRAnalysis(atr=Decimal("10")) # 0.2 * 10 = 2.0 max distance
    
    # Mock a candle where close is way below EMA 20
    # EMA 20 = 90. Close = 80. Distance = 10. Max distance = 2.0. Too far.
    snapshot.candles = [
        Candle(
            timestamp=datetime.utcnow(), instrument="BTC/USD", timeframe=Timeframe.M1, source="test",
            open=Decimal("95"), high=Decimal("96"), low=Decimal("79"), close=Decimal("80"), volume=Decimal("100")
        )
    ]
    
    pullback_analyzer = PullbackAnalyzer()
    result = pullback_analyzer.analyze(snapshot)
    
    assert result.is_pullback is False
