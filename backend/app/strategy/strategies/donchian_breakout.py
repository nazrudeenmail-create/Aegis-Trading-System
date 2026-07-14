from decimal import Decimal

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class DonchianChannelBreakoutStrategy(BaseStrategy):
    name = "Donchian Channel Breakout"
    version = "1.0"
    description = "Enters on breakout of the 20-period Donchian Channel, filtered by ADX."
    
    primary_timeframe = Timeframe.M15
    required_timeframes = [
        Timeframe.D1,
        Timeframe.H4,
        Timeframe.M15
    ]

    def get_profile(self):
        from app.strategy.profiles.donchian_breakout import get_donchian_breakout_profile
        return get_donchian_breakout_profile()

    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        daily = mtf_context.get(Timeframe.D1)
        h4 = mtf_context.get(Timeframe.H4)
        m15 = mtf_context.get(Timeframe.M15)
        
        passed_rules = []
        total_rules = 5
        
        def fail(rule: str, reason: str) -> StrategyResult:
            from app.strategy.models import RuleFailure
            return StrategyResult(
                is_valid=False,
                total_rules=total_rules,
                passed_rules=passed_rules,
                failed_rule=RuleFailure(rule=rule, reason=reason)
            )
        
        if not all([daily, h4, m15]):
            return fail("Data Availability", "Missing or invalid timeframes")
            
        if not m15.is_valid or not m15.candles:
            return fail("Data Availability", "Invalid primary snapshot or no candles")
            
        latest_daily_candle = daily.candles[-1]
        latest_m15_candle = m15.candles[-1]

        # 1. Daily Trend
        if not daily.ema or daily.ema.ema_200 is None:
            return fail("Daily Trend", "Daily EMA200 missing")
            
        is_long_macro = latest_daily_candle.close > daily.ema.ema_200
        is_short_macro = latest_daily_candle.close < daily.ema.ema_200
        
        if not is_long_macro and not is_short_macro:
             return fail("Daily Trend", "Daily close exactly equals EMA200")
             
        passed_rules.append("Daily Trend")
        intended_direction = TradeDirection.LONG if is_long_macro else TradeDirection.SHORT
        
        # 2. 4H Trend Confirmation
        if not h4.ema or h4.ema.ema_20 is None or h4.ema.ema_50 is None or h4.ema.ema_200 is None:
             return fail("4H Trend", "4H EMA data missing")
             
        if intended_direction == TradeDirection.LONG:
             if not (h4.ema.ema_20 > h4.ema.ema_50 and h4.ema.ema_50 > h4.ema.ema_200):
                 return fail("4H Trend", "4H EMA structure not bullish")
        else:
             if not (h4.ema.ema_20 < h4.ema.ema_50 and h4.ema.ema_50 < h4.ema.ema_200):
                 return fail("4H Trend", "4H EMA structure not bearish")
                 
        passed_rules.append("4H Trend")
                 
        # 3. 4H Trend Strength
        if h4.adx is None or h4.adx.adx is None or h4.adx.adx < Decimal("25"):
             return fail("4H Trend Strength", "4H ADX is weak (<25)")
             
        passed_rules.append("4H Trend Strength")
             
        # 4. 15M Breakout Execution
        if not m15.donchian:
            return fail("15M Breakout Execution", "Donchian analysis is missing on 15M")
            
        if intended_direction == TradeDirection.LONG:
            if not m15.donchian.is_breakout_up:
                return fail("15M Breakout Execution", "No Donchian breakout UP")
            if m15.donchian.upper_band is None or latest_m15_candle.close <= m15.donchian.upper_band:
                return fail("15M Breakout Execution", "Close is not above upper band")
            if not m15.candle or not m15.candle.is_bullish:
                return fail("15M Breakout Execution", "15M breakout candle is not bullish")
        else:
            if not m15.donchian.is_breakout_down:
                return fail("15M Breakout Execution", "No Donchian breakout DOWN")
            if m15.donchian.lower_band is None or latest_m15_candle.close >= m15.donchian.lower_band:
                return fail("15M Breakout Execution", "Close is not below lower band")
            if not m15.candle or not m15.candle.is_bearish:
                return fail("15M Breakout Execution", "15M breakout candle is not bearish")
                
        passed_rules.append("15M Breakout Execution")
                
        # 5. Volume Confirmation
        if not m15.volume or m15.volume.current_volume is None or m15.volume.average_volume is None:
             return fail("Volume Confirmation", "15M Volume data missing")
             
        if m15.volume.current_volume <= m15.volume.average_volume:
             return fail("Volume Confirmation", "15M Volume confirmation failed (Current <= Avg)")
             
        passed_rules.append("Volume Confirmation")

        # Stop Loss at breakout candle extreme
        if not m15.atr or m15.atr.atr is None:
            return fail("Risk Management", "Missing ATR for stop loss buffer")
            
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
        return StrategyResult(
            is_valid=True,
            candidate=candidate,
            total_rules=total_rules,
            passed_rules=passed_rules
        )
