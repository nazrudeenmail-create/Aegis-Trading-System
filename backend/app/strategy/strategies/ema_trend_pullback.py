from decimal import Decimal
from typing import List

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.market_analysis.enums import MarketRegime, EMAAlignment
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class EMATrendPullbackStrategy(BaseStrategy):
    name = "EMA Trend Pullback"
    version = "1.0"
    description = "Trades pullbacks to the 20 EMA in the direction of the 200 EMA trend."
    
    primary_timeframe = Timeframe.M15
    required_timeframes = [
        Timeframe.H4,
        Timeframe.H1,
        Timeframe.M15,
    ]

    def get_profile(self):
        from app.strategy.profiles.ema_pullback import get_ema_pullback_profile
        return get_ema_pullback_profile()

    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        h4_snapshot = mtf_context.get(Timeframe.H4)
        h1_snapshot = mtf_context.get(Timeframe.H1)
        m15_snapshot = mtf_context.get(Timeframe.M15)
        
        passed_rules = []
        total_rules = 6
        
        def fail(rule: str, reason: str) -> StrategyResult:
            from app.strategy.models import RuleFailure
            return StrategyResult(
                is_valid=False,
                total_rules=total_rules,
                passed_rules=passed_rules,
                failed_rule=RuleFailure(rule=rule, reason=reason)
            )
        
        if not h4_snapshot or not h1_snapshot or not m15_snapshot:
            return fail("Data Availability", "Missing required timeframes in context")
            
        if not m15_snapshot.is_valid or not m15_snapshot.candles:
            return fail("Data Availability", "Invalid primary snapshot or no candles")

        # 1. Higher Timeframe Alignment Check
        if not h4_snapshot.trend or not h1_snapshot.trend:
            return fail("Higher Timeframe Alignment", "Missing trend data on higher timeframes")
            
        h4_alignment = h4_snapshot.trend.ema_alignment
        h1_alignment = h1_snapshot.trend.ema_alignment
        
        if h4_alignment == EMAAlignment.MIXED or h1_alignment == EMAAlignment.MIXED:
             return fail("Higher Timeframe Alignment", "Higher timeframe trends are MIXED")
             
        if h4_alignment != h1_alignment:
             return fail("Higher Timeframe Alignment", "4H and 1H trends do not align")
             
        passed_rules.append("Higher Timeframe Alignment")
        intended_direction = TradeDirection.LONG if h4_alignment == EMAAlignment.BULLISH else TradeDirection.SHORT

        # 2. Market Regime Check on Primary Timeframe (15M)
        if not m15_snapshot.regime or m15_snapshot.regime.regime != MarketRegime.TRENDING:
            return fail("Primary Market Regime", "15M market is not trending")
            
        if not m15_snapshot.trend or not m15_snapshot.adx or not m15_snapshot.pullback or not m15_snapshot.swing or not m15_snapshot.candle or not m15_snapshot.volume or not m15_snapshot.atr:
            return fail("Primary Market Regime", "Missing required market analysis data on 15M")
            
        if m15_snapshot.trend.ema_alignment != h4_alignment:
             return fail("Primary Market Regime", "15M trend does not align with HTF trend")
             
        passed_rules.append("Primary Market Regime")

        # 3. Trend Strength Check
        if m15_snapshot.adx.adx is None or m15_snapshot.adx.adx < Decimal("25"):
            return fail("Trend Strength", "15M Trend strength (ADX) is weak")
            
        passed_rules.append("Trend Strength")
            
        # 4. Pullback Quality Check
        if not m15_snapshot.pullback.is_pullback or m15_snapshot.pullback.distance_from_ema20 is None:
            return fail("Pullback Quality", "No valid pullback detected on 15M")
            
        if m15_snapshot.atr.atr is None:
            return fail("Pullback Quality", "ATR is missing on 15M")
            
        max_distance = Decimal("0.2") * m15_snapshot.atr.atr
        if m15_snapshot.pullback.distance_from_ema20 > max_distance:
            return fail("Pullback Quality", f"Pullback too far from EMA20: {m15_snapshot.pullback.distance_from_ema20} > {max_distance}")
            
        passed_rules.append("Pullback Quality")
            
        # 5. Volume Confirmation Check
        if m15_snapshot.volume.current_volume is None or m15_snapshot.volume.average_volume is None:
            return fail("Volume Confirmation", "Volume data missing on 15M")
        if m15_snapshot.volume.current_volume <= m15_snapshot.volume.average_volume:
            return fail("Volume Confirmation", "Insufficient volume confirmation on 15M")
            
        passed_rules.append("Volume Confirmation")

        latest_candle = m15_snapshot.candles[-1]
        
        if intended_direction == TradeDirection.LONG:
            result = self._evaluate_long(m15_snapshot, latest_candle, passed_rules, total_rules, fail)
        else:
            result = self._evaluate_short(m15_snapshot, latest_candle, passed_rules, total_rules, fail)
            
        return result
            
    def _evaluate_long(self, snapshot: MarketSnapshot, latest_candle, passed_rules, total_rules, fail) -> StrategyResult:
        # Market Structure Check (Long)
        if snapshot.swing.swing_low is None:
             return fail("Market Structure", "No swing low found for structure check")
             
        # Entry Confirmation Check (Candle)
        if not snapshot.candle.is_bullish:
             return fail("Entry Confirmation", "Confirmation candle is not bullish")
             
        if snapshot.ema.ema_20 is not None and latest_candle.close <= snapshot.ema.ema_20:
             return fail("Entry Confirmation", "Confirmation candle closed below EMA20")
             
        passed_rules.append("Entry Confirmation")
             
        # Generate BUY Candidate
        stop_loss = snapshot.swing.swing_low - (Decimal("0.5") * snapshot.atr.atr)
        
        candidate = TradeCandidate(
            strategy_name=self.name,
            strategy_version=self.version,
            symbol=latest_candle.instrument,
            direction=TradeDirection.LONG,
            entry_price=latest_candle.close,
            stop_loss=stop_loss,
            market_conditions={
                "trend": "BULLISH",
                "adx": float(snapshot.adx.adx),
                "ema_alignment": snapshot.trend.ema_alignment.value
            }
        )
        return StrategyResult(
            is_valid=True,
            candidate=candidate,
            total_rules=total_rules,
            passed_rules=passed_rules
        )
        
    def _evaluate_short(self, snapshot: MarketSnapshot, latest_candle, passed_rules, total_rules, fail) -> StrategyResult:
        # Market Structure Check (Short)
        if snapshot.swing.swing_high is None:
             return fail("Market Structure", "No swing high found for structure check")
             
        # Entry Confirmation Check (Candle)
        if not snapshot.candle.is_bearish:
             return fail("Entry Confirmation", "Confirmation candle is not bearish")
             
        if snapshot.ema.ema_20 is not None and latest_candle.close >= snapshot.ema.ema_20:
             return fail("Entry Confirmation", "Confirmation candle closed above EMA20")
             
        passed_rules.append("Entry Confirmation")
             
        # Generate SELL Candidate
        stop_loss = snapshot.swing.swing_high + (Decimal("0.5") * snapshot.atr.atr)
        
        candidate = TradeCandidate(
            strategy_name=self.name,
            strategy_version=self.version,
            symbol=latest_candle.instrument,
            direction=TradeDirection.SHORT,
            entry_price=latest_candle.close,
            stop_loss=stop_loss,
            market_conditions={
                "trend": "BEARISH",
                "adx": float(snapshot.adx.adx),
                "ema_alignment": snapshot.trend.ema_alignment.value
            }
        )
        return StrategyResult(
            is_valid=True,
            candidate=candidate,
            total_rules=total_rules,
            passed_rules=passed_rules
        )
