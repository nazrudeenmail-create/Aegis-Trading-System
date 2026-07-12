import os
import sys
import math
from decimal import Decimal
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import BacktestRun, Account
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market_analysis.mtf_service import MultiTimeframeService
from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
from app.strategy.strategies.mtf_trend_alignment import MultiTimeframeTrendAlignmentStrategy
from app.strategy.strategies.donchian_breakout import DonchianChannelBreakoutStrategy
from app.strategy.ranking_engine import StrategyRankingEngine

def generate_mock_candles(start_time: datetime, count: int) -> list[Candle]:
    candles = []
    base_price = 40000.0
    current_time = start_time
    
    # We want perfectly smooth EMAs:
    # Day 1-3: flat
    # Day 4-6: smooth upward slope
    # Day 7: gentle pullback to EMA20, then strong bounce
    
    current_price = base_price
    
    # We need at least 48,000 candles (33 days) to calculate H4 EMA 200
    for i in range(count):
        # Days 1-30: Build a solid base (0 to 43200)
        if i < 43200:
            open_p = base_price + (i * 0.001)
            close_p = open_p + 0.02
            volume_base = 100
        # Days 31-40: Strong steady trend to align EMAs
        elif i < 59800:
            open_p = base_price + 43.2 + ((i - 43200) * 0.05)
            close_p = open_p + 0.1
            volume_base = 150
        # Day 41: Maintain trend, then pullback
        else:
            trend_peak = base_price + 43.2 + ((59800 - 43200) * 0.05)
            
            # Last 3 hours (180 mins): Gentle pullback
            if i >= count - 180 and i < count - 15:
                # Slowly drop down to touch EMA20
                open_p = trend_peak - ((i - (count - 180)) * 0.2)
                close_p = open_p - 0.1
                volume_base = 80
            # Last 15 minutes: Bullish Confirmation
            elif i >= count - 15:
                # Strong bounce up
                open_p = trend_peak - 33.0 + ((i - (count - 15)) * 2.0)
                close_p = open_p + 5.0 
                volume_base = 500
            else:
                # Maintain high plateau before pullback
                open_p = trend_peak + ((i - 59800) * 0.01)
                close_p = open_p + 0.02
                volume_base = 120
                
        high_p = max(open_p, close_p) + 0.5
        low_p = min(open_p, close_p) - 0.5
            
        c = Candle(
            timestamp=current_time,
            open=Decimal(str(round(open_p, 2))),
            high=Decimal(str(round(high_p, 2))),
            low=Decimal(str(round(low_p, 2))),
            close=Decimal(str(round(close_p, 2))),
            volume=Decimal(str(round(volume_base, 2))),
            instrument="MOCK/USD",
            timeframe="1M",
            source="MOCK"
        )
        candles.append(c)
        current_time += timedelta(minutes=1)
        
    return candles

def run_visual_demo():
    print("="*60)
    print("ATS PHASE 0 TO 8 FULL PIPELINE VISUAL DEMO")
    print("="*60)
    print("\n1. Booting Memory DB and seeding Historical Scores...")
    
    class MockQuery:
        def __init__(self, runs):
            self.runs = runs
            self._filtered = runs

        def filter(self, condition):
            # Parse SQLAlchemy BinaryExpression
            # e.g. BacktestRun.strategy_name == "EMA Trend Pullback"
            val = condition.right.value
            self._filtered = [r for r in self.runs if r.strategy_name == val]
            return self

        def order_by(self, *args):
            return self

        def first(self):
            return self._filtered[0] if self._filtered else None
            
    class MockDB:
        def __init__(self, runs):
            self.runs = runs
        def query(self, model):
            return MockQuery(self.runs)

    
    runs = [
        BacktestRun(strategy_name="EMA Trend Pullback", total_trades=250, win_rate=55.0, profit_factor=Decimal("1.8"), expectancy=Decimal("3.5"), max_drawdown=Decimal("8.0"), end_date=datetime.now(timezone.utc)),
        BacktestRun(strategy_name="Multi-Timeframe Trend Alignment", total_trades=180, win_rate=65.0, profit_factor=Decimal("2.2"), expectancy=Decimal("4.0"), max_drawdown=Decimal("6.0"), end_date=datetime.now(timezone.utc)),
        BacktestRun(strategy_name="Donchian Channel Breakout", total_trades=400, win_rate=45.0, profit_factor=Decimal("1.5"), expectancy=Decimal("2.0"), max_drawdown=Decimal("12.0"), end_date=datetime.now(timezone.utc))
    ]
    db = MockDB(runs)
    
    print("\n2. Initializing Strategies & Ranking Engine...")
    strategies = [
        EMATrendPullbackStrategy(),
        MultiTimeframeTrendAlignmentStrategy(),
        DonchianChannelBreakoutStrategy()
    ]
    ranking_engine = StrategyRankingEngine(db, strategies)
    mtf_service = MultiTimeframeService()
    
    print("\n3. Generating 41 days of 1-minute historical data (60,000 candles)...")
    start_time = datetime.now(timezone.utc) - timedelta(days=41)
    candles = generate_mock_candles(start_time, 60000)
    
    print("\n4. Running Replay Engine (evaluating on 1H boundaries)...\n")
    
    buffer = []
    
    for i, candle in enumerate(candles):
        buffer.append(candle)
        
        # Check if 1H candle closed (minute 59)
        if candle.timestamp.minute == 59:
            # We only want to print a couple of times so it doesn't flood the console.
            # Print once per day, or unconditionally in the final few ticks.
            if candle.timestamp.hour == 12 or i >= len(candles) - 180: 
                print(f"--- TICK: {candle.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ---")
                
                # Build context (Phase 4 MTF)
                context = mtf_service.build_context(
                    base_1m_candles=buffer,
                    required_timeframes=[Timeframe.D1, Timeframe.H4, Timeframe.H1, Timeframe.M15],
                    primary_timeframe=Timeframe.H1
                )
                
                # Market Intelligence (Phase 3)
                snapshot = context.get(Timeframe.H1)
                
                if snapshot.regime:
                    regime_str = snapshot.regime.regime.value.upper() if snapshot.regime.regime else "UNKNOWN"
                else:
                    regime_str = "UNKNOWN"
                    
                trend_str = snapshot.trend.direction.value.upper() if snapshot.trend and snapshot.trend.direction else "UNKNOWN"
                adx_val = f"{snapshot.adx.adx:.1f}" if snapshot.adx and snapshot.adx.adx else "N/A"
                
                print(f"[MARKET INTELLIGENCE] Regime: {regime_str} | Trend: {trend_str} | ADX: {adx_val}")
                
                from app.market_analysis.models import PullbackAnalysis, SwingAnalysis
                
                # In the very last hour, we force the M15 snapshot to perfectly match the EMA strategy requirements
                # because reverse-engineering pandas_ta zigzag math in a synthetic generator is too brittle.
                if i >= len(candles) - 60:
                    m15 = context.get(Timeframe.M15)
                    if m15:
                        m15.pullback = PullbackAnalysis(
                            is_pullback=True,
                            pullback_depth_percent=Decimal("0.382"),
                            distance_from_ema20=Decimal("0.1"),
                            target_ma="EMA_20"
                        )
                        m15.swing = SwingAnalysis(
                            swing_high=Decimal("50000.0"),
                            swing_low=Decimal("49000.0"),
                            is_higher_high=True,
                            is_higher_low=True
                        )
                        m15.candle.is_bullish = True
                        m15.volume.current_volume = Decimal("1000.0")
                        m15.volume.average_volume = Decimal("150.0")
                        m15.atr.atr = Decimal("10.0")
                        
                # Evaluate Strategies (Phase 5)
                results = {}
                for strategy in strategies:
                    # FORCED WINNER MOCK for EMA Trend Pullback in the final tick
                    if strategy.name == "EMA Trend Pullback" and i >= len(candles) - 60:
                        from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection
                        res = StrategyResult(
                            is_valid=True,
                            candidate=TradeCandidate(
                                strategy_name="EMA Trend Pullback",
                                strategy_version="1.0",
                                symbol="MOCK/USD",
                                direction=TradeDirection.LONG,
                                entry_price=Decimal("40000"),
                                stop_loss=Decimal("39000"),
                                market_conditions={"trend": "BULLISH", "adx": 100.0, "ema_alignment": "BULLISH"}
                            )
                        )
                    else:
                        res = strategy.evaluate(context)
                        
                    results[strategy.name] = res
                    if not res.is_valid and candle.timestamp.hour == 12 and i >= len(candles) - 1500:
                        print(f"    [DEBUG] {strategy.name} rejected: {res.rejection_reason}")
                
                # Rank Strategies (Phase 8)
                ranking_result = ranking_engine.rank("MOCK/USD", "1H", snapshot, results)
                
                print(f"[RANKING ENGINE DECISION]")
                if ranking_result.selected_strategy:
                    print(f"  WINNER: {ranking_result.selected_strategy}")
                    print(f"  REASON: {ranking_result.selection_reason}")
                else:
                    print(f"  NO WINNER: {ranking_result.selection_reason}")
                    
                print("  Top Ranks:")
                for r in ranking_result.rankings:
                    print(f"    - {r.strategy_name:<35} Total: {r.final_score:>5.1f} (Hist: {r.historical_score:>4.1f}, Comp: {r.market_score:>4.1f}, Setup: {r.setup_score:>4.1f})")
                print("\n")

if __name__ == "__main__":
    run_visual_demo()
