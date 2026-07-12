from decimal import Decimal
from typing import List

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.market_analysis.enums import MarketRegime, EMAAlignment
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class MultiTimeframeTrendAlignmentStrategy(BaseStrategy):
    name = "Multi-Timeframe Trend Alignment"
    version = "1.1"
    description = "Requires trend alignment across Daily, 4H, 1H, and 15M."
    
    primary_timeframe = Timeframe.M15
    required_timeframes = [
        Timeframe.D1,
        Timeframe.H4,
        Timeframe.H1,
        Timeframe.M15,
    ]

    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        daily = mtf_context.get(Timeframe.D1)
        h4 = mtf_context.get(Timeframe.H4)
        h1 = mtf_context.get(Timeframe.H1)
        m15 = mtf_context.get(Timeframe.M15)
        
        if not all([daily, h4, h1, m15]):
            return StrategyResult(is_valid=False, rejection_reason="Missing required timeframes")
            
        if not m15.is_valid or not m15.candles:
            return StrategyResult(is_valid=False, rejection_reason="Invalid primary snapshot or no candles")
            
        latest_candle_m15 = m15.candles[-1]

        # Determine macro trend from Daily price vs EMA200
        if not daily.ema or daily.ema.ema_200 is None:
             return StrategyResult(is_valid=False, rejection_reason="Daily EMA200 missing")
             
        latest_daily_candle = daily.candles[-1]
        is_long_macro = latest_daily_candle.close > daily.ema.ema_200
        is_short_macro = latest_daily_candle.close < daily.ema.ema_200
        
        if not is_long_macro and not is_short_macro:
             return StrategyResult(is_valid=False, rejection_reason="Daily close exactly equals EMA200, no trend")
             
        intended_direction = TradeDirection.LONG if is_long_macro else TradeDirection.SHORT
        
        # 4H Confirmation
        if not h4.regime or h4.regime.regime != MarketRegime.TRENDING:
             return StrategyResult(is_valid=False, rejection_reason="4H Market Regime is not TRENDING")
             
        if not h4.ema or h4.ema.ema_20 is None or h4.ema.ema_50 is None or h4.ema.ema_200 is None:
             return StrategyResult(is_valid=False, rejection_reason="4H EMA data missing")
             
        if intended_direction == TradeDirection.LONG:
             if not (h4.ema.ema_20 > h4.ema.ema_50 and h4.ema.ema_50 > h4.ema.ema_200):
                 return StrategyResult(is_valid=False, rejection_reason="4H EMA structure not bullish")
        else:
             if not (h4.ema.ema_20 < h4.ema.ema_50 and h4.ema.ema_50 < h4.ema.ema_200):
                 return StrategyResult(is_valid=False, rejection_reason="4H EMA structure not bearish")
                 
        # 1H Confirmation
        if not h1.ema or h1.ema.ema_9 is None or h1.ema.ema_21 is None:
             return StrategyResult(is_valid=False, rejection_reason="1H EMA data missing")
             
        if intended_direction == TradeDirection.LONG:
             if not (h1.ema.ema_9 > h1.ema.ema_21):
                 return StrategyResult(is_valid=False, rejection_reason="1H EMA structure not bullish")
        else:
             if not (h1.ema.ema_9 < h1.ema.ema_21):
                 return StrategyResult(is_valid=False, rejection_reason="1H EMA structure not bearish")
                 
        # 15M Entry Execution
        if not m15.ema or m15.ema.ema_9 is None or m15.ema.ema_21 is None:
             return StrategyResult(is_valid=False, rejection_reason="15M EMA data missing")
             
        if intended_direction == TradeDirection.LONG:
             if not (m15.ema.ema_9 > m15.ema.ema_21):
                 return StrategyResult(is_valid=False, rejection_reason="15M EMA structure not bullish")
        else:
             if not (m15.ema.ema_9 < m15.ema.ema_21):
                 return StrategyResult(is_valid=False, rejection_reason="15M EMA structure not bearish")
                 
        if m15.adx is None or m15.adx.adx is None or m15.adx.adx < Decimal("25"):
             return StrategyResult(is_valid=False, rejection_reason="15M ADX is weak")
             
        if not m15.volume or m15.volume.current_volume is None or m15.volume.average_volume is None:
             return StrategyResult(is_valid=False, rejection_reason="15M Volume data missing")
             
        if m15.volume.current_volume <= m15.volume.average_volume:
             return StrategyResult(is_valid=False, rejection_reason="15M Volume confirmation failed")
             
        if not m15.candle:
             return StrategyResult(is_valid=False, rejection_reason="15M Candle data missing")
             
        if intended_direction == TradeDirection.LONG:
             if not m15.candle.is_bullish:
                 return StrategyResult(is_valid=False, rejection_reason="15M candle is not bullish")
        else:
             if not m15.candle.is_bearish:
                 return StrategyResult(is_valid=False, rejection_reason="15M candle is not bearish")

        # 3. Market Structure & Stop Loss (15M)
        if intended_direction == TradeDirection.LONG:
            if not m15.swing or m15.swing.swing_low is None:
                return StrategyResult(is_valid=False, rejection_reason="No swing low found for stop loss on 15M")
            base_sl = m15.swing.swing_low
        else:
            if not m15.swing or m15.swing.swing_high is None:
                return StrategyResult(is_valid=False, rejection_reason="No swing high found for stop loss on 15M")
            base_sl = m15.swing.swing_high

        # Provide a buffer using ATR
        if not m15.atr or m15.atr.atr is None:
            return StrategyResult(is_valid=False, rejection_reason="Missing ATR for stop loss buffer")
            
        atr_buffer = Decimal("0.5") * m15.atr.atr
        stop_loss = base_sl - atr_buffer if intended_direction == TradeDirection.LONG else base_sl + atr_buffer
        
        candidate = TradeCandidate(
            strategy_name=self.name,
            strategy_version=self.version,
            symbol=latest_candle_m15.instrument,
            direction=intended_direction,
            entry_price=latest_candle_m15.close,
            stop_loss=stop_loss,
            market_conditions={
                "trend": "100% ALIGNED",
                "daily_trend": "BULLISH" if is_long_macro else "BEARISH",
                "entry_trigger": "BULLISH CANDLE" if intended_direction == TradeDirection.LONG else "BEARISH CANDLE"
            }
        )
        return StrategyResult(is_valid=True, candidate=candidate)
