import sys
import os
from decimal import Decimal

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.risk.models import RiskProfile
from app.risk.engine import RiskEngine
from app.strategy.models import TradeCandidate, TradeDirection

def run_demo():
    print("--- Phase 6: Risk Management Engine Demo ---")
    
    candidate = TradeCandidate(
        strategy_name="EMA Trend Pullback",
        strategy_version="1.0",
        symbol="BTCUSDT",
        direction=TradeDirection.LONG,
        entry_price=Decimal("100.0"),
        stop_loss=Decimal("95.0"),
        market_conditions={}
    )
    print(f"\nTrade Candidate: LONG BTCUSDT Entry={candidate.entry_price} Stop={candidate.stop_loss}")
    
    # 1. Normal Profile
    print("\n[Normal Profile: $10k, 1% Risk, 5% Max Open Risk]")
    profile = RiskProfile(account_balance=Decimal("10000.0"))
    engine = RiskEngine()
    context = {'current_open_risk_fiat': Decimal("200.0"), 'daily_loss_fiat': Decimal("0.0")}
    assessment = engine.evaluate(candidate, profile, context)
    print(f"Approved: {assessment.is_approved}")
    if assessment.is_approved:
        print(f"Position Size: {assessment.position_size}")
        print(f"Fiat at Risk: ${assessment.risk_amount_fiat}")
    
    # 2. Exposure Limit Hit
    print("\n[Exposure Limit Scenario: Current open risk is already 4.5% ($450)]")
    context_high_risk = {'current_open_risk_fiat': Decimal("450.0"), 'daily_loss_fiat': Decimal("0.0")}
    assessment2 = engine.evaluate(candidate, profile, context_high_risk)
    print(f"Approved: {assessment2.is_approved}")
    if not assessment2.is_approved:
        print(f"Reason: {assessment2.rejection_reason}")

    # 3. High Risk Mode Bypassed
    print("\n[High Risk Mode Bypassed Scenario: Aggressive Trader]")
    aggressive_profile = RiskProfile(
        account_balance=Decimal("10000.0"),
        max_open_risk_percent=Decimal("30.0"), # User configures high limit
        allow_high_risk_mode=True
    )
    assessment3 = engine.evaluate(candidate, aggressive_profile, context_high_risk)
    print(f"Approved: {assessment3.is_approved}")
    if assessment3.is_approved:
        print(f"Position Size: {assessment3.position_size}")
        print(f"Warnings: {assessment3.warnings}")

if __name__ == "__main__":
    run_demo()
