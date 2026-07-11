"""
Demo script to visualize the output of the Phase 5 Strategy Engine.
It uses the dummy candles and the MarketAnalysisService to generate a MarketSnapshot,
then passes it to the StrategyEngine to generate TradeCandidates.
"""

from decimal import Decimal
from datetime import datetime, timezone
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.market.domain.candle import Candle
from app.market_analysis.service import MarketAnalysisService
from app.strategy.engine import StrategyEngine

def run_demo():
    print("=" * 60)
    print(" PHASE 5: STRATEGY ENGINE DEMO")
    print("=" * 60)
    
    # 1. Create realistic dummy candles for a perfect long setup
    print("\n[1] Fetching market data...")
    now = datetime.now(timezone.utc)
    
    candles = []
    # Build 50 dummy candles to give pandas-ta enough data for EMA200 (wait, pandas-ta needs 200 candles for EMA200!)
    # Actually, the MarketAnalysisService uses a fallback if there's not enough data, but let's provide 250 dummy candles.
    
    # Generate 250 candles simulating an uptrend, with a recent pullback
    base_price = Decimal("100.0")
    for i in range(250):
        # Gradual uptrend
        trend_factor = Decimal(str(i * 0.1))
        
        open_price = base_price + trend_factor
        close_price = open_price + Decimal("0.5") # Bullish most of the time
        high_price = close_price + Decimal("0.2")
        low_price = open_price - Decimal("0.2")
        
        # Simulate the recent pullback at the very end
        if i >= 245:
            # Drop price to simulate pullback
            open_price = close_price - Decimal("2.0")
            close_price = open_price - Decimal("1.0")
            high_price = open_price + Decimal("0.1")
            low_price = close_price - Decimal("0.5")
            
        # The last candle is the confirmation candle (Bullish engulfing bouncing off EMA20)
        if i == 249:
            open_price = low_price # Open low
            close_price = open_price + Decimal("3.0") # Close high, above previous
            high_price = close_price + Decimal("0.5")
            low_price = open_price - Decimal("0.5")
        
        candle = Candle(
            timestamp=now,
            instrument="BTC/USD",
            timeframe="15M",
            source="demo",
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=Decimal("150.0") if i == 249 else Decimal("100.0") # Volume spike on confirmation
        )
        candles.append(candle)
    
    print(f"Generated {len(candles)} dummy candles simulating an uptrend and pullback.")
    
    # 2. Run Market Analysis (Phase 4)
    print("\n[2] Running Market Analysis (Tier 1 & 2)...")
    analysis_service = MarketAnalysisService()
    snapshot = analysis_service.analyze(candles)
    
    # We must explicitly set some Tier 2 facts that rely on complex calculations that might fail with our simple dummy data
    # (e.g., ADX needs very specific True Range variance, Swing needs specific pivot highs/lows)
    # Let's override the snapshot with perfect setup conditions to guarantee the strategy fires.
    from app.market_analysis.models import (
        TrendAnalysis, MarketRegimeAnalysis, EMAAlignmentAnalysis, 
        PullbackAnalysis, SwingAnalysis, ADXAnalysis, CandleAnalysis
    )
    from app.market_analysis.enums import TrendDirection, TrendStrength, EMAAlignment, MarketRegime
    
    snapshot.regime = MarketRegimeAnalysis(regime=MarketRegime.TRENDING, is_tradable=True)
    snapshot.ema_alignment = EMAAlignmentAnalysis(timeframe="15M", alignment=EMAAlignment.BULLISH, stack=["EMA9", "EMA20"], strength=TrendStrength.STRONG)
    snapshot.adx = ADXAnalysis(adx=Decimal("35.0"), dmp=Decimal("40.0"), dmn=Decimal("10.0"))
    snapshot.pullback = PullbackAnalysis(is_pullback=True, distance_from_ema20=Decimal("0.5"), target_ma="ema_20")
    snapshot.swing = SwingAnalysis(swing_high=Decimal("150.0"), swing_low=Decimal("120.0"))
    snapshot.candle = CandleAnalysis(is_bullish=True, is_bearish=False, is_engulfing=True, is_inside_bar=False, is_rejection=False)
    
    # We must also inject ATR and EMA because the strategy pulls values from them directly
    from app.market_analysis.models import ATRAnalysis, EMAAnalysis
    snapshot.atr = ATRAnalysis(atr=Decimal("5.0"))
    snapshot.ema = EMAAnalysis(ema_9=Decimal("101.0"), ema_20=Decimal("100.0"), ema_21=Decimal("99.0"), ema_50=Decimal("90.0"), ema_100=Decimal("80.0"), ema_200=Decimal("70.0"))
    
    print(f"Market Regime: {snapshot.regime.regime.name}")
    print(f"Trend Direction: {snapshot.ema_alignment.alignment.name}")
    print(f"ADX Strength: {snapshot.adx.adx}")
    print(f"Pullback Detected: {snapshot.pullback.is_pullback} (Dist: {snapshot.pullback.distance_from_ema20})")
    
    # 3. Run Strategy Engine (Phase 5)
    print("\n[3] Running Strategy Engine...")
    strategy_engine = StrategyEngine()
    candidates = strategy_engine.evaluate_all(snapshot)
    
    print(f"Strategies Executed: {len(strategy_engine.strategies)}")
    print(f"Valid Trade Candidates Found: {len(candidates)}")
    
    # 4. Display Results
    if candidates:
        print("\n" + "=" * 60)
        print(" TRADE CANDIDATES (PASSED TO RANKING/RISK)")
        print("=" * 60)
        
        for idx, candidate in enumerate(candidates, 1):
            print(f"\nCandidate #{idx}")
            print(f"  Strategy: {candidate.strategy_name} (v{candidate.strategy_version})")
            print(f"  Symbol:   {candidate.symbol}")
            print(f"  Action:   {candidate.direction.name}")
            print(f"  Entry:    ${candidate.entry_price}")
            print(f"  Stop:     ${candidate.stop_loss}")
            print("  Context:")
            for key, value in candidate.market_conditions.items():
                print(f"    - {key}: {value}")
    else:
        print("\nNo valid trade candidates found. All strategies rejected the market conditions.")
        
if __name__ == "__main__":
    run_demo()
