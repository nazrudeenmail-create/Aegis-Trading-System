import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from datetime import datetime, timezone
from decimal import Decimal
from pprint import pprint

from app.market.domain.candle import Candle
from app.market_analysis.service import MarketAnalysisService

def generate_demo_candles(count: int, base_price: float = 50000.0, trend: float = 10.0) -> list[Candle]:
    """Generate mock BTC/USD candles showing a strong uptrend."""
    candles = []
    current_price = base_price
    for _ in range(count):
        close_price = current_price + trend
        candles.append(
            Candle(
                timestamp=datetime.now(timezone.utc),
                instrument="BTC/USD",
                timeframe="1M",
                open=Decimal(str(current_price)),
                high=Decimal(str(max(current_price, close_price) + 25.0)),
                low=Decimal(str(min(current_price, close_price) - 15.0)),
                close=Decimal(str(close_price)),
                volume=Decimal("150.5"),
                source="mock_data_provider"
            )
        )
        current_price = close_price
    return candles

def run_demo():
    print("==================================================")
    print(" Aegis Trading System - Phase 4 Demo ")
    print("==================================================")
    
    print("\n[1] Initializing MarketAnalysisService...")
    service = MarketAnalysisService()
    
    print("\n[2] Generating 250 mock 1M candles (Uptrending BTC/USD)...")
    candles = generate_demo_candles(250)
    
    print(f"    - First Close: ${candles[0].close}")
    print(f"    - Last Close:  ${candles[-1].close}")
    
    print("\n[3] Orchestrating Phase A (Math) and Phase B (Intelligence)...")
    snapshot = service.analyze(candles)
    
    print("\n[DONE] Execution Complete! Generating Intelligence Report...\n")
    
    print("--------------------------------------------------")
    print(" MARKET SNAPSHOT REPORT")
    print("--------------------------------------------------")
    print(f"Snapshot Time: {snapshot.generated_at}")
    print(f"Data Valid:    {snapshot.is_valid}")
    print(f"Errors Found:  {len(snapshot.analysis_errors)}")
    if snapshot.analysis_errors:
        print(f"Errors: {snapshot.analysis_errors}")
        
    print("\n--- TIER 1: FACTS (Raw Math) ---")
    print(f"EMA 9:   ${snapshot.ema.ema_9 if snapshot.ema else 'N/A'}")
    print(f"EMA 20:  ${snapshot.ema.ema_20 if snapshot.ema else 'N/A'}")
    print(f"EMA 50:  ${snapshot.ema.ema_50 if snapshot.ema else 'N/A'}")
    print(f"EMA 200: ${snapshot.ema.ema_200 if snapshot.ema else 'N/A'}")
    print(f"ATR (14): {snapshot.atr.atr if snapshot.atr else 'N/A'}")
    
    print("\n--- TIER 2: INTELLIGENCE (Context) ---")
    if snapshot.ema_alignment:
        print(f"EMA Alignment:    {snapshot.ema_alignment.alignment.name}")
        print(f"EMA Stack:        {', '.join(snapshot.ema_alignment.stack)}")
    else:
        print("EMA Alignment: N/A")
        
    if snapshot.trend:
        print(f"Trend Direction:  {snapshot.trend.direction.name}")
        print(f"Trend Strength:   {snapshot.trend.strength.name}")
    else:
        print("Trend: N/A")
        
    if snapshot.regime:
        print(f"Market Regime:    {snapshot.regime.regime.name}")
        print(f"Is Tradable?      {'[YES]' if snapshot.regime.is_tradable else '[NO] (Capital Protection Active)'}")
    else:
        print("Regime: N/A")
        
    if snapshot.pullback:
        print(f"Is Pullback?      {'[YES]' if snapshot.pullback.is_pullback else '[NO]'}")
        if snapshot.pullback.is_pullback:
            print(f"Target MA:        {snapshot.pullback.target_ma}")
    else:
        print("Pullback: N/A")
        
    print("\n==================================================")
    print("Demo finished successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_demo()
