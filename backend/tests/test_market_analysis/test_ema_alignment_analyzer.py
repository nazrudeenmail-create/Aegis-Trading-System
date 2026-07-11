import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.market.domain.candle import Candle
from app.market_analysis.models import MarketSnapshot, EMAAnalysis
from app.market_analysis.analyzers.ema_alignment_analyzer import EMAAlignmentAnalyzer
from app.market_analysis.enums import EMAAlignment, TrendStrength

def test_ema_alignment_bullish():
    analyzer = EMAAlignmentAnalyzer()
    snapshot = MarketSnapshot(
        candles=[
            Candle(
                timestamp=datetime.now(timezone.utc), instrument="BTC/USD", timeframe="4H", source="test",
                open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("100"), volume=Decimal("10")
            )
        ]
    )
    
    # Simulate Bullish Alignment: 9 > 20 > 50 > 100 > 200
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("100"),
        ema_20=Decimal("90"),
        ema_21=Decimal("89"),
        ema_50=Decimal("80"),
        ema_100=Decimal("70"),
        ema_200=Decimal("60")
    )
    
    result = analyzer.analyze(snapshot)
    
    assert result is not None
    assert result.alignment == EMAAlignment.BULLISH
    assert result.strength == TrendStrength.STRONG
    assert result.timeframe == "4H"
    assert result.stack == ["EMA9", "EMA20", "EMA50", "EMA100", "EMA200"]

def test_ema_alignment_bearish():
    analyzer = EMAAlignmentAnalyzer()
    snapshot = MarketSnapshot(
        candles=[
            Candle(
                timestamp=datetime.now(timezone.utc), instrument="BTC/USD", timeframe="1H", source="test",
                open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("100"), volume=Decimal("10")
            )
        ]
    )
    
    # Simulate Bearish Alignment: 200 > 100 > 50 > 20 > 9
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("60"),
        ema_20=Decimal("70"),
        ema_21=Decimal("71"),
        ema_50=Decimal("80"),
        ema_100=Decimal("90"),
        ema_200=Decimal("100")
    )
    
    result = analyzer.analyze(snapshot)
    
    assert result is not None
    assert result.alignment == EMAAlignment.BEARISH
    assert result.strength == TrendStrength.STRONG
    assert result.stack == ["EMA200", "EMA100", "EMA50", "EMA20", "EMA9"]

def test_ema_alignment_mixed():
    analyzer = EMAAlignmentAnalyzer()
    snapshot = MarketSnapshot(
        candles=[
            Candle(
                timestamp=datetime.now(timezone.utc), instrument="BTC/USD", timeframe="1M", source="test",
                open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("100"), volume=Decimal("10")
            )
        ]
    )
    
    # Simulate Mixed Alignment: 50 > 9 > 200 > 20 > 100
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("90"),
        ema_20=Decimal("70"),
        ema_21=Decimal("71"),
        ema_50=Decimal("100"),
        ema_100=Decimal("60"),
        ema_200=Decimal("80")
    )
    
    result = analyzer.analyze(snapshot)
    
    assert result is not None
    assert result.alignment == EMAAlignment.MIXED
    assert result.strength == TrendStrength.WEAK
