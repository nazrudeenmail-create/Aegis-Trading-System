from typing import List
from datetime import datetime

from app.backtest.models import BacktestConfig
from app.backtest.simulated_broker import SimulatedBroker
from app.market.domain.candle import Candle
from app.strategy.base import BaseStrategy
from app.market_analysis.mtf_service import MultiTimeframeService
from app.market.domain.timeframe import Timeframe


class BacktestEngine:
    """
    Executes historical market replay.
    Ensures strict look-ahead bias protection by only evaluating strategies
    when the primary timeframe candle formally closes.
    """
    def __init__(self, config: BacktestConfig, broker: SimulatedBroker, strategy: BaseStrategy):
        self.config = config
        self.broker = broker
        self.strategy = strategy
        self.mtf_service = MultiTimeframeService()
        
    def run(self, historical_1m_candles: List[Candle]):
        """
        Runs the simulation tick-by-tick using 1-minute historical candles.
        """
        # Ensure chronological order and filter by date range
        candles = sorted(historical_1m_candles, key=lambda c: c.timestamp)
        candles = [c for c in candles if self.config.start_date <= c.timestamp <= self.config.end_date]
        
        buffer: List[Candle] = []
        
        primary_tf_minutes = self._get_minutes(self.strategy.primary_timeframe)
        
        for candle in candles:
            # Add to chronological knowledge base and trim to ~200 days (288,000 mins) to prevent O(n^2) bloat
            buffer.append(candle)
            if len(buffer) > 288000:
                buffer = buffer[-288000:]
            
            # Step 1: Intra-bar stop loss / take profit checks
            # Evaluates SL/TP precisely inside the 1-minute tick (even if primary TF is 1H)
            self.broker.process_1m_candle(candle)
            
            # Step 2: Check if primary timeframe closed (Look-Ahead Bias Protection)
            # A 15M candle from 10:00 to 10:15 consists of 1M candles from 10:00 to 10:14.
            # When the 10:14 candle finishes, the 15M candle is officially closed.
            minute_of_day = candle.timestamp.hour * 60 + candle.timestamp.minute
            
            # Did the primary timeframe just close on this tick?
            if (minute_of_day + 1) % primary_tf_minutes == 0:
                
                # Build context strictly using the buffer up to this tick
                context = self.mtf_service.build_context(
                    base_1m_candles=buffer,
                    required_timeframes=self.strategy.required_timeframes,
                    primary_timeframe=self.strategy.primary_timeframe
                )
                
                # Strategy evaluation
                result = self.strategy.evaluate(context)
                
                if result.is_valid and result.candidate:
                    # Submit to broker for immediate filling (using simulated spread/slippage)
                    self.broker.submit_candidate(result.candidate, candle.timestamp)
                    
        # Backtest Complete. Compute statistics
        from app.backtest.statistics import BacktestStatistics
        stats = BacktestStatistics(self.config.initial_balance, self.broker.closed_trades).calculate()
        
        return stats
                    
    def _get_minutes(self, tf: Timeframe) -> int:
        mapping = {
            Timeframe.M1: 1,
            Timeframe.M5: 5,
            Timeframe.M15: 15,
            Timeframe.H1: 60,
            Timeframe.H4: 240,
            Timeframe.D1: 1440,
        }
        return mapping.get(tf, 1)
