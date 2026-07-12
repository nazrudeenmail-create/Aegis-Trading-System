from decimal import Decimal

from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import MultiTimeframeContext, MarketSnapshot
from app.strategy.base import BaseStrategy
from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection

class DonchianChannelBreakoutStrategy(BaseStrategy):
    name = "Donchian Channel Breakout"
    version = "1.0"
    description = "Enters on a breakout of the 20-period Donchian Channel."
    
    primary_timeframe = Timeframe.D1
    required_timeframes = [
        Timeframe.D1
    ]

    def evaluate(self, mtf_context: MultiTimeframeContext) -> StrategyResult:
        daily = mtf_context.get(Timeframe.D1)
        
        if not daily or not daily.is_valid or not daily.candles:
            return StrategyResult(is_valid=False, rejection_reason="Missing or invalid Daily timeframe")
            
        if not daily.donchian:
            return StrategyResult(is_valid=False, rejection_reason="Donchian analysis is missing")
            
        is_breakout_up = daily.donchian.is_breakout_up
        is_breakout_down = daily.donchian.is_breakout_down
        
        if not is_breakout_up and not is_breakout_down:
            return StrategyResult(is_valid=False, rejection_reason="No Donchian breakout detected")
            
        intended_direction = TradeDirection.LONG if is_breakout_up else TradeDirection.SHORT
        latest_candle = daily.candles[-1]
        
        # Stop Loss at the opposite band
        # For a LONG breakout, stop loss is the lower band.
        # For a SHORT breakout, stop loss is the upper band.
        if intended_direction == TradeDirection.LONG:
            if daily.donchian.lower_band is None:
                return StrategyResult(is_valid=False, rejection_reason="Missing lower band for stop loss")
            stop_loss = daily.donchian.lower_band
        else:
            if daily.donchian.upper_band is None:
                return StrategyResult(is_valid=False, rejection_reason="Missing upper band for stop loss")
            stop_loss = daily.donchian.upper_band

        # Ensure the stop loss is logical (e.g., lower band is below entry price)
        if intended_direction == TradeDirection.LONG and stop_loss >= latest_candle.close:
            return StrategyResult(is_valid=False, rejection_reason="Invalid stop loss for LONG (>= entry)")
        if intended_direction == TradeDirection.SHORT and stop_loss <= latest_candle.close:
            return StrategyResult(is_valid=False, rejection_reason="Invalid stop loss for SHORT (<= entry)")

        candidate = TradeCandidate(
            strategy_name=self.name,
            strategy_version=self.version,
            symbol=latest_candle.instrument,
            direction=intended_direction,
            entry_price=latest_candle.close,
            stop_loss=stop_loss,
            market_conditions={
                "donchian_breakout": "UP" if is_breakout_up else "DOWN",
                "channel_width": float(daily.donchian.channel_width) if daily.donchian.channel_width else None
            }
        )
        return StrategyResult(is_valid=True, candidate=candidate)
