import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.market.domain.candle import Candle
from app.market_analysis.models import (
    MarketSnapshot, EMAAnalysis, ATRAnalysis, ADXAnalysis, VolumeAnalysis, 
    CandleAnalysis, SwingAnalysis, TrendAnalysis, MarketRegimeAnalysis, 
    MomentumAnalysis, PullbackAnalysis, VolatilityAnalysis
)
from app.market_analysis.enums import (
    TrendDirection, TrendStrength, EMAAlignment, MarketRegime, VolatilityState, MomentumState
)

def create_mock_snapshot(
    regime=MarketRegime.TRENDING, 
    alignment=EMAAlignment.BULLISH,
    adx_val="30.0", 
    is_pullback=True, 
    dist_from_ema="0.5", 
    atr_val="5.0",
    swing_low="90.0",
    swing_high="110.0",
    candle_bullish=True,
    candle_bearish=False,
    vol_current="150",
    vol_avg="100",
    close_price="105.0",
    ema20_val="100.0"
):
    candle = Candle(
        timestamp=datetime.now(timezone.utc), instrument="BTC/USD", timeframe="1H", source="test",
        open=Decimal("100"), high=Decimal("110"), low=Decimal("95"), close=Decimal(close_price), volume=Decimal(vol_current)
    )
    
    snapshot = MarketSnapshot(candles=[candle])
    
    snapshot.ema = EMAAnalysis(
        ema_9=Decimal("100"), ema_20=Decimal(ema20_val), ema_21=Decimal("99"), ema_50=Decimal("80"), ema_100=Decimal("70"), ema_200=Decimal("60")
    )
    snapshot.atr = ATRAnalysis(atr=Decimal(atr_val))
    snapshot.adx = ADXAnalysis(adx=Decimal(adx_val), dmp=Decimal("30"), dmn=Decimal("10"))
    snapshot.volume = VolumeAnalysis(current_volume=Decimal(vol_current), average_volume=Decimal(vol_avg))
    snapshot.candle = CandleAnalysis(is_bullish=candle_bullish, is_bearish=candle_bearish, is_engulfing=True, is_inside_bar=False, is_rejection=False)
    snapshot.swing = SwingAnalysis(swing_high=Decimal(swing_high), swing_low=Decimal(swing_low))
    

    snapshot.trend = TrendAnalysis(direction=TrendDirection.BULLISH, strength=TrendStrength.STRONG, ema_alignment=alignment)
    snapshot.regime = MarketRegimeAnalysis(regime=regime, is_tradable=True)
    snapshot.momentum = MomentumAnalysis(momentum=MomentumState.BULLISH)
    snapshot.pullback = PullbackAnalysis(is_pullback=is_pullback, distance_from_ema20=Decimal(dist_from_ema), target_ma="ema_20")
    snapshot.volatility = VolatilityAnalysis(state=VolatilityState.NORMAL)
    
    return snapshot
