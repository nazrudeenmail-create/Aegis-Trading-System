from decimal import Decimal
from typing import List

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.market_analysis.enums import MarketRegime, EMAAlignment
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class MultiTimeframeTrendAlignmentStrategy(BaseStrategy):
    name = "Multi-Timeframe Trend Alignment"
    version = "1.0"
    description = "Requires 100% trend alignment across 4H, 1H, 15M, and 5M. Enters on a 5M engulfing candle."
    
    primary_timeframe = Timeframe.M5
    required_timeframes = [
        Timeframe.H4,
        Timeframe.H1,
        Timeframe.M15,
        Timeframe.M5,
    ]

    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        h4 = mtf_context.get(Timeframe.H4)
        h1 = mtf_context.get(Timeframe.H1)
        m15 = mtf_context.get(Timeframe.M15)
        m5 = mtf_context.get(Timeframe.M5)
        
        if not all([h4, h1, m15, m5]):
            return StrategyResult(is_valid=False, rejection_reason="Missing required timeframes")
            
        if not m5.is_valid or not m5.candles:
            return StrategyResult(is_valid=False, rejection_reason="Invalid primary snapshot or no candles")

        # 1. 100% Trend Alignment Check
        snapshots = [h4, h1, m15, m5]
        for tf_snap in snapshots:
            if not tf_snap.trend:
                return StrategyResult(is_valid=False, rejection_reason="Missing trend data")
                
        alignments = [s.trend.ema_alignment for s in snapshots]
        
        if any(a == EMAAlignment.MIXED for a in alignments):
            return StrategyResult(is_valid=False, rejection_reason="One or more timeframes have MIXED trend")
            
        # All must be identical
        first_alignment = alignments[0]
        if not all(a == first_alignment for a in alignments):
            return StrategyResult(is_valid=False, rejection_reason="Trends are not 100% aligned across all timeframes")
            
        intended_direction = TradeDirection.LONG if first_alignment == EMAAlignment.BULLISH else TradeDirection.SHORT
        
        # 2. Entry Signal (5M Engulfing)
        if not m5.candle:
            return StrategyResult(is_valid=False, rejection_reason="Missing candle data on 5M")
            
        if intended_direction == TradeDirection.LONG:
            if not m5.candle.is_engulfing or not m5.candle.is_bullish:
                return StrategyResult(is_valid=False, rejection_reason="No bullish engulfing on 5M")
        else:
            if not m5.candle.is_engulfing or not m5.candle.is_bearish:
                return StrategyResult(is_valid=False, rejection_reason="No bearish engulfing on 5M")

        # 3. Market Structure & Stop Loss (5M)
        if intended_direction == TradeDirection.LONG:
            if not m5.swing or m5.swing.swing_low is None:
                return StrategyResult(is_valid=False, rejection_reason="No swing low found for stop loss on 5M")
            base_sl = m5.swing.swing_low
        else:
            if not m5.swing or m5.swing.swing_high is None:
                return StrategyResult(is_valid=False, rejection_reason="No swing high found for stop loss on 5M")
            base_sl = m5.swing.swing_high

        # Provide a buffer using ATR
        if not m5.atr or m5.atr.atr is None:
            return StrategyResult(is_valid=False, rejection_reason="Missing ATR for stop loss buffer")
            
        atr_buffer = Decimal("0.5") * m5.atr.atr
        stop_loss = base_sl - atr_buffer if intended_direction == TradeDirection.LONG else base_sl + atr_buffer
        
        latest_candle = m5.candles[-1]
        
        candidate = TradeCandidate(
            strategy_name=self.name,
            strategy_version=self.version,
            symbol=latest_candle.instrument,
            direction=intended_direction,
            entry_price=latest_candle.close,
            stop_loss=stop_loss,
            market_conditions={
                "trend": "100% ALIGNED",
                "alignment": first_alignment.value,
                "entry_trigger": "ENGULFING"
            }
        )
        return StrategyResult(is_valid=True, candidate=candidate)
