import pytest
from decimal import Decimal
from app.market_analysis.enums import MarketRegime, EMAAlignment
from app.strategy.strategies.mtf_trend_alignment import MultiTimeframeTrendAlignmentStrategy
from app.strategy.models import TradeDirection
from tests.test_strategy.conftest import create_mock_mtf_context
from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import EMAAnalysis

def test_mtf_trend_alignment_long_valid():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        adx_val="30.0",
        vol_current="150",
        vol_avg="100",
        candle_bullish=True,
        swing_low="90.0",
        atr_val="5.0"
    )
    # Set Daily Price > EMA200
    daily = context.get(Timeframe.D1)
    daily.candles[-1] = daily.candles[-1].model_copy(update={"close": Decimal("150")})
    daily.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # Set 4H EMA structure
    h4 = context.get(Timeframe.H4)
    h4.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # Set 1H EMA structure
    h1 = context.get(Timeframe.H1)
    h1.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # Set 15M EMA structure
    m15 = context.get(Timeframe.M15)
    m15.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    strategy = MultiTimeframeTrendAlignmentStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is True
    assert result.candidate is not None
    assert result.candidate.direction == TradeDirection.LONG
    assert result.candidate.stop_loss == Decimal("90.0") - (Decimal("0.5") * Decimal("5.0"))

def test_reject_when_timeframes_conflict():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        adx_val="30.0",
        vol_current="150",
        vol_avg="100",
        candle_bullish=True,
        swing_low="90.0",
        atr_val="5.0"
    )
    # Daily bullish
    daily = context.get(Timeframe.D1)
    daily.candles[-1] = daily.candles[-1].model_copy(update={"close": Decimal("150")})
    daily.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # 4H bullish
    h4 = context.get(Timeframe.H4)
    h4.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # 1H bullish
    h1 = context.get(Timeframe.H1)
    h1.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # 15M bearish
    m15 = context.get(Timeframe.M15)
    m15.ema = EMAAnalysis(ema_9=Decimal("100"), ema_20=Decimal("110"), ema_21=Decimal("111"), ema_50=Decimal("120"), ema_100=Decimal("130"), ema_200=Decimal("140"))
    
    strategy = MultiTimeframeTrendAlignmentStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert "15M EMA structure not bullish" in result.rejection_reason

def test_mtf_trend_alignment_weak_adx():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        adx_val="20.0",
        vol_current="150",
        vol_avg="100",
        candle_bullish=True,
        swing_low="90.0",
        atr_val="5.0"
    )
    
    daily = context.get(Timeframe.D1)
    daily.candles[-1] = daily.candles[-1].model_copy(update={"close": Decimal("150")})
    daily.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    h4 = context.get(Timeframe.H4)
    h4.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    h1 = context.get(Timeframe.H1)
    h1.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    m15 = context.get(Timeframe.M15)
    m15.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    strategy = MultiTimeframeTrendAlignmentStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert "15M ADX is weak" in result.rejection_reason
