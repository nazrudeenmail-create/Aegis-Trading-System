import pytest
from decimal import Decimal
from app.market_analysis.enums import MarketRegime, EMAAlignment
from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
from app.strategy.models import TradeDirection
from tests.test_strategy.conftest import create_mock_mtf_context

def test_ema_pullback_long_valid():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        alignment=EMAAlignment.BULLISH,
        adx_val="30.0",
        is_pullback=True,
        dist_from_ema="0.5", # max is 0.2 * 5.0 = 1.0
        atr_val="5.0",
        swing_low="90.0",
        candle_bullish=True,
        vol_current="150",
        vol_avg="100",
        close_price="105.0",
        ema20_val="100.0"
    )
    
    strategy = EMATrendPullbackStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is True
    assert result.candidate is not None
    assert result.candidate.direction == TradeDirection.LONG
    assert result.candidate.stop_loss == Decimal("90.0") - (Decimal("0.5") * Decimal("5.0")) # 87.5
    assert result.candidate.market_conditions["trend"] == "BULLISH"

def test_ema_pullback_short_valid():
    context = create_mock_mtf_context(
        regime=MarketRegime.TRENDING,
        alignment=EMAAlignment.BEARISH,
        adx_val="30.0",
        is_pullback=True,
        dist_from_ema="0.5",
        atr_val="5.0",
        swing_high="110.0",
        candle_bullish=False,
        candle_bearish=True,
        vol_current="150",
        vol_avg="100",
        close_price="95.0",
        ema20_val="100.0"
    )
    
    strategy = EMATrendPullbackStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is True
    assert result.candidate is not None
    assert result.candidate.direction == TradeDirection.SHORT
    assert result.candidate.stop_loss == Decimal("110.0") + (Decimal("0.5") * Decimal("5.0")) # 112.5
    assert result.candidate.market_conditions["trend"] == "BEARISH"

def test_ema_pullback_invalid_regime():
    context = create_mock_mtf_context(regime=MarketRegime.RANGING)
    strategy = EMATrendPullbackStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert result.rejection_reason == "15M market is not trending"

def test_ema_pullback_weak_adx():
    context = create_mock_mtf_context(adx_val="20.0")
    strategy = EMATrendPullbackStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert result.rejection_reason == "15M Trend strength (ADX) is weak"

def test_ema_pullback_invalid_pullback_distance():
    context = create_mock_mtf_context(dist_from_ema="1.5", atr_val="5.0") # max is 1.0
    strategy = EMATrendPullbackStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert "Pullback too far from EMA20" in result.rejection_reason

def test_ema_pullback_invalid_volume():
    context = create_mock_mtf_context(vol_current="90", vol_avg="100")
    strategy = EMATrendPullbackStrategy()
    result = strategy.evaluate(context)
    
    assert result.is_valid is False
    assert result.rejection_reason == "Insufficient volume confirmation on 15M"
