from decimal import Decimal
from app.market_analysis.models import MarketSnapshot
from app.market_analysis.enums import MarketRegime, EMAAlignment
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class EMATrendPullbackStrategy(BaseStrategy):
    name = "EMA Trend Pullback"
    version = "2.1"
    description = "Enters in the direction of the trend after a pullback to the EMA20."

    def evaluate(self, snapshot: MarketSnapshot) -> StrategyResult:
        if not snapshot.is_valid or not snapshot.candles:
            return StrategyResult(is_valid=False, rejection_reason="Invalid snapshot or no candles")

        # 1. Market Regime Check
        if not snapshot.regime or snapshot.regime.regime != MarketRegime.TRENDING:
            return StrategyResult(is_valid=False, rejection_reason="Market is not trending")
            
        # Ensure all required components exist
        if not snapshot.trend or not snapshot.adx or not snapshot.pullback or not snapshot.swing or not snapshot.candle or not snapshot.volume or not snapshot.atr:
            return StrategyResult(is_valid=False, rejection_reason="Missing required market analysis data")
            
        # 2. Trend Strength Check
        if snapshot.adx.adx is None or snapshot.adx.adx < Decimal("25"):
            return StrategyResult(is_valid=False, rejection_reason="Trend strength (ADX) is weak")
            
        # 3. Pullback Quality Check
        if not snapshot.pullback.is_pullback or snapshot.pullback.distance_from_ema20 is None:
            return StrategyResult(is_valid=False, rejection_reason="No valid pullback detected")
            
        if snapshot.atr.atr is None:
            return StrategyResult(is_valid=False, rejection_reason="ATR is missing")
            
        max_distance = Decimal("0.2") * snapshot.atr.atr
        if snapshot.pullback.distance_from_ema20 > max_distance:
            return StrategyResult(is_valid=False, rejection_reason=f"Pullback too far from EMA20: {snapshot.pullback.distance_from_ema20} > {max_distance}")
            
        # 4. Volume Confirmation Check
        if snapshot.volume.current_volume is None or snapshot.volume.average_volume is None:
            return StrategyResult(is_valid=False, rejection_reason="Volume data missing")
        if snapshot.volume.current_volume <= snapshot.volume.average_volume:
            return StrategyResult(is_valid=False, rejection_reason="Insufficient volume confirmation")

        latest_candle = snapshot.candles[-1]
        
        # Branch for LONG vs SHORT based on EMA Alignment
        if snapshot.trend.ema_alignment == EMAAlignment.BULLISH:
            return self._evaluate_long(snapshot, latest_candle)
        elif snapshot.trend.ema_alignment == EMAAlignment.BEARISH:
            return self._evaluate_short(snapshot, latest_candle)
        else:
            return StrategyResult(is_valid=False, rejection_reason="EMA Alignment is MIXED")
            
    def _evaluate_long(self, snapshot: MarketSnapshot, latest_candle) -> StrategyResult:
        # Market Structure Check (Long)
        if snapshot.swing.swing_low is None:
             return StrategyResult(is_valid=False, rejection_reason="No swing low found for structure check")
             
        # Entry Confirmation Check (Candle)
        if not snapshot.candle.is_bullish:
             return StrategyResult(is_valid=False, rejection_reason="Confirmation candle is not bullish")
             
        if snapshot.ema.ema_20 is not None and latest_candle.close <= snapshot.ema.ema_20:
             return StrategyResult(is_valid=False, rejection_reason="Confirmation candle closed below EMA20")
             
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
        return StrategyResult(is_valid=True, candidate=candidate)
        
    def _evaluate_short(self, snapshot: MarketSnapshot, latest_candle) -> StrategyResult:
        # Market Structure Check (Short)
        if snapshot.swing.swing_high is None:
             return StrategyResult(is_valid=False, rejection_reason="No swing high found for structure check")
             
        # Entry Confirmation Check (Candle)
        if not snapshot.candle.is_bearish:
             return StrategyResult(is_valid=False, rejection_reason="Confirmation candle is not bearish")
             
        if snapshot.ema.ema_20 is not None and latest_candle.close >= snapshot.ema.ema_20:
             return StrategyResult(is_valid=False, rejection_reason="Confirmation candle closed above EMA20")
             
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
        return StrategyResult(is_valid=True, candidate=candidate)
