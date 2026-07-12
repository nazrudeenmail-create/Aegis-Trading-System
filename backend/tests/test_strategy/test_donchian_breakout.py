import pytest
from decimal import Decimal
from app.market_analysis.enums import MarketRegime
from app.strategy.strategies.donchian_breakout import DonchianChannelBreakoutStrategy
from app.strategy.models import TradeDirection
from tests.test_strategy.conftest import create_mock_mtf_context
from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import EMAAnalysis, DonchianAnalysis

def test_donchian_breakout_long_valid():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        adx_val="30.0",
        vol_current="150",
        vol_avg="100",
        candle_bullish=True,
        atr_val="5.0"
    )
    
    # Daily Price > EMA200
    daily = context.get(Timeframe.D1)
    daily.candles[-1] = daily.candles[-1].model_copy(update={"close": Decimal("150")})
    daily.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # 4H EMA structure and ADX
    h4 = context.get(Timeframe.H4)
    h4.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    # 15M Breakout
    m15 = context.get(Timeframe.M15)
    m15.donchian = DonchianAnalysis(
        upper_band=Decimal("100.0"),
        lower_band=Decimal("50.0"),
        middle_band=Decimal("75.0"),
        channel_width=Decimal("50.0"),
        is_breakout_up=True,
        is_breakout_down=False
    )
    m15.candles[-1] = m15.candles[-1].model_copy(update={"close": Decimal("105.0"), "low": Decimal("95.0")})
    
    strategy = DonchianChannelBreakoutStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is True
    assert result.candidate is not None
    assert result.candidate.direction == TradeDirection.LONG
    assert result.candidate.stop_loss == Decimal("95.0") - (Decimal("0.5") * Decimal("5.0"))

def test_reject_breakout_without_close_confirmation():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        adx_val="30.0",
        vol_current="150",
        vol_avg="100",
        candle_bullish=True,
        atr_val="5.0"
    )
    
    daily = context.get(Timeframe.D1)
    daily.candles[-1] = daily.candles[-1].model_copy(update={"close": Decimal("150")})
    daily.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    h4 = context.get(Timeframe.H4)
    h4.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    m15 = context.get(Timeframe.M15)
    m15.donchian = DonchianAnalysis(
        upper_band=Decimal("100.0"),
        lower_band=Decimal("50.0"),
        middle_band=Decimal("75.0"),
        channel_width=Decimal("50.0"),
        is_breakout_up=True,  # Might have broken intraday
        is_breakout_down=False
    )
    # Price touches above Donchian upper band but Close < Upper Band
    m15.candles[-1] = m15.candles[-1].model_copy(update={
        "high": Decimal("105.0"), 
        "close": Decimal("95.0"), 
        "low": Decimal("90.0")
    })
    
    strategy = DonchianChannelBreakoutStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert "Close is not above upper band" in result.rejection_reason

def test_donchian_breakout_low_volume():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        adx_val="30.0",
        vol_current="90",  # Low volume
        vol_avg="100",
        candle_bullish=True,
        atr_val="5.0"
    )
    
    daily = context.get(Timeframe.D1)
    daily.candles[-1] = daily.candles[-1].model_copy(update={"close": Decimal("150")})
    daily.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    h4 = context.get(Timeframe.H4)
    h4.ema = EMAAnalysis(ema_9=Decimal("140"), ema_20=Decimal("130"), ema_21=Decimal("129"), ema_50=Decimal("120"), ema_100=Decimal("110"), ema_200=Decimal("100"))
    
    m15 = context.get(Timeframe.M15)
    m15.donchian = DonchianAnalysis(
        upper_band=Decimal("100.0"),
        lower_band=Decimal("50.0"),
        middle_band=Decimal("75.0"),
        channel_width=Decimal("50.0"),
        is_breakout_up=True,
        is_breakout_down=False
    )
    m15.candles[-1] = m15.candles[-1].model_copy(update={"close": Decimal("105.0"), "low": Decimal("95.0")})
    
    strategy = DonchianChannelBreakoutStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert "15M Volume confirmation failed" in result.rejection_reason
