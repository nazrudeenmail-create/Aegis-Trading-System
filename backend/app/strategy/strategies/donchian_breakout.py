from decimal import Decimal

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class DonchianChannelBreakoutStrategy(BaseStrategy):
    name = "Donchian Channel Breakout"
    version = "1.1"
    description = "Enters on a breakout of the 20-period Donchian Channel on the 15M timeframe, aligned with Daily and 4H."
    
    primary_timeframe = Timeframe.M15
    required_timeframes = [
        Timeframe.D1,
        Timeframe.H4,
        Timeframe.M15
    ]

    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        daily = mtf_context.get(Timeframe.D1)
        h4 = mtf_context.get(Timeframe.H4)
        m15 = mtf_context.get(Timeframe.M15)
        
        if not all([daily, h4, m15]):
            return StrategyResult(is_valid=False, rejection_reason="Missing or invalid timeframes")
            
        if not m15.is_valid or not m15.candles:
            return StrategyResult(is_valid=False, rejection_reason="Invalid primary snapshot or no candles")
            
        latest_daily_candle = daily.candles[-1]
        latest_m15_candle = m15.candles[-1]

        # 1. Daily Trend
        if not daily.ema or daily.ema.ema_200 is None:
            return StrategyResult(is_valid=False, rejection_reason="Daily EMA200 missing")
            
        is_long_macro = latest_daily_candle.close > daily.ema.ema_200
        is_short_macro = latest_daily_candle.close < daily.ema.ema_200
        
        if not is_long_macro and not is_short_macro:
             return StrategyResult(is_valid=False, rejection_reason="Daily close exactly equals EMA200")
             
        intended_direction = TradeDirection.LONG if is_long_macro else TradeDirection.SHORT
        
        # 2. 4H Trend Confirmation
        if not h4.ema or h4.ema.ema_20 is None or h4.ema.ema_50 is None or h4.ema.ema_200 is None:
             return StrategyResult(is_valid=False, rejection_reason="4H EMA data missing")
             
        if intended_direction == TradeDirection.LONG:
             if not (h4.ema.ema_20 > h4.ema.ema_50 and h4.ema.ema_50 > h4.ema.ema_200):
                 return StrategyResult(is_valid=False, rejection_reason="4H EMA structure not bullish")
        else:
             if not (h4.ema.ema_20 < h4.ema.ema_50 and h4.ema.ema_50 < h4.ema.ema_200):
                 return StrategyResult(is_valid=False, rejection_reason="4H EMA structure not bearish")
                 
        if h4.adx is None or h4.adx.adx is None or h4.adx.adx < Decimal("25"):
             return StrategyResult(is_valid=False, rejection_reason="4H ADX is weak")
             
        # 3. 15M Breakout Execution
        if not m15.donchian:
            return StrategyResult(is_valid=False, rejection_reason="Donchian analysis is missing on 15M")
            
        if intended_direction == TradeDirection.LONG:
            if not m15.donchian.is_breakout_up:
                return StrategyResult(is_valid=False, rejection_reason="No Donchian breakout UP")
            if m15.donchian.upper_band is None or latest_m15_candle.close <= m15.donchian.upper_band:
                return StrategyResult(is_valid=False, rejection_reason="Close is not above upper band")
            if not m15.candle or not m15.candle.is_bullish:
                return StrategyResult(is_valid=False, rejection_reason="15M breakout candle is not bullish")
        else:
            if not m15.donchian.is_breakout_down:
                return StrategyResult(is_valid=False, rejection_reason="No Donchian breakout DOWN")
            if m15.donchian.lower_band is None or latest_m15_candle.close >= m15.donchian.lower_band:
                return StrategyResult(is_valid=False, rejection_reason="Close is not below lower band")
            if not m15.candle or not m15.candle.is_bearish:
                return StrategyResult(is_valid=False, rejection_reason="15M breakout candle is not bearish")
                
        # Volume Confirmation
        if not m15.volume or m15.volume.current_volume is None or m15.volume.average_volume is None:
             return StrategyResult(is_valid=False, rejection_reason="15M Volume data missing")
             
        if m15.volume.current_volume <= m15.volume.average_volume:
             return StrategyResult(is_valid=False, rejection_reason="15M Volume confirmation failed")

        # Stop Loss at breakout candle extreme
        if not m15.atr or m15.atr.atr is None:
            return StrategyResult(is_valid=False, rejection_reason="Missing ATR for stop loss buffer")
            
        atr_buffer = Decimal("0.5") * m15.atr.atr
        
        if intended_direction == TradeDirection.LONG:
            stop_loss = latest_m15_candle.low - atr_buffer
        else:
            stop_loss = latest_m15_candle.high + atr_buffer

        candidate = TradeCandidate(
            strategy_name=self.name,
            strategy_version=self.version,
            symbol=latest_m15_candle.instrument,
            direction=intended_direction,
            entry_price=latest_m15_candle.close,
            stop_loss=stop_loss,
            market_conditions={
                "donchian_breakout": "UP" if intended_direction == TradeDirection.LONG else "DOWN",
                "daily_trend": "BULLISH" if intended_direction == TradeDirection.LONG else "BEARISH"
            }
        )
        return StrategyResult(is_valid=True, candidate=candidate)
