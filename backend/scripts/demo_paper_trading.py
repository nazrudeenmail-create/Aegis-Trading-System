"""
Aegis Trading System - Phase 9 Paper Trading Demo
"""

import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.strategy.models import TradeCandidate, TradeDirection
from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.execution.models.paper_config import PaperTradingConfig, ExecutionSimulationConfig
from app.execution.broker.paper_broker import PaperBroker
from app.execution.engine import ExecutionEngine
from app.execution.paper_monitor import PaperTradingMonitor


async def run_paper_trading_demo():
    print("="*60)
    print("ATS PHASE 9: PAPER TRADING & EXECUTION ENGINE DEMO")
    print("="*60)

    # 1. Initialize Components
    print("\n1. Initializing Engines & Broker...")
    
    sim_config = ExecutionSimulationConfig(
        slippage_enabled=True,
        slippage_percentage=Decimal("0.0005"), # 0.05%
        commission_enabled=True,
        commission_rate=Decimal("1.50"),
        execution_delay_ms=0
    )
    
    paper_config = PaperTradingConfig(
        enabled=True,
        starting_balance=Decimal("10000.0"),
        max_duration_days=30,
        required_trade_count=1, # Setting to 1 for demo
        minimum_win_rate=50.0,
        maximum_drawdown=5.0
    )
    
    broker = PaperBroker(initial_balance=paper_config.starting_balance, config=sim_config)
    await broker.connect()
    
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker=broker, risk_engine=risk_engine)
    monitor = PaperTradingMonitor(config=paper_config)
    
    # 2. Simulate Strategy Selection
    print("\n2. Simulating Ranking Engine Selection...")
    
    candidate = TradeCandidate(
        strategy_name="EMA Trend Pullback",
        strategy_version="1.0",
        symbol="BTC/USD",
        direction=TradeDirection.LONG,
        entry_price=Decimal("60000.0"),
        stop_loss=Decimal("59000.0"),
        take_profit=Decimal("62000.0"),
        market_conditions={"regime": "TRENDING", "adx": 35.5}
    )
    
    ranking_score = 81.8
    risk_profile = RiskProfile(
        account_balance=broker.balance,
        max_risk_per_trade_percent=Decimal("1.0"), 
        max_open_risk_percent=Decimal("3.0"), 
        max_daily_loss_percent=Decimal("5.0")
    )
    risk_context = {"current_open_risk_fiat": Decimal("0.0"), "daily_loss_fiat": Decimal("0.0"), "account_balance": broker.balance}
    
    print(f"   Selected: {candidate.strategy_name} ({candidate.direction.value}) on {candidate.symbol} @ {candidate.entry_price}")
    
    # We must seed the broker with the current market price so MARKET order can fill
    current_time = datetime.now(timezone.utc)
    broker.tick("BTC/USD", price=Decimal("60000.0"), timestamp=current_time)
    
    # 3. Execution
    print("\n3. Executing Trade...")
    result = await execution_engine.execute(
        candidate=candidate,
        ranking_score=ranking_score,
        risk_profile=risk_profile,
        risk_context=risk_context
    )
    
    if result:
        print(f"   Order {result.order_id} -> Status: {result.status.value}")
        print(f"   Filled Quantity: {result.filled_quantity} @ Price: {result.filled_price:.2f}")
    else:
        print("   Execution failed or rejected.")
        return
        
    print(f"   Broker Balance: ${await broker.get_account_balance():.2f}")
        
    # 4. Simulate Market Movement (Tick to hit Take Profit)
    print("\n4. Simulating Market Price Updates...")
    print("   Price moves to 61,000...")
    current_time += timedelta(minutes=10)
    broker.tick("BTC/USD", price=Decimal("61000.0"), timestamp=current_time)
    
    print("   Price moves to 62,500 (Hits TP!)...")
    current_time += timedelta(minutes=10)
    broker.tick("BTC/USD", price=Decimal("62500.0"), timestamp=current_time)
    
    print(f"   Broker Balance: ${await broker.get_account_balance():.2f}")
    
    # 5. Monitor Evaluation
    print("\n5. Generating Validation Report...")
    closed_trades = broker.get_closed_trades()
    report = monitor.generate_report(
        strategy_name="EMA Trend Pullback",
        trades=closed_trades,
        days_running=15
    )
    
    print("\n" + "="*40)
    print("PAPER TRADING REPORT")
    print("="*40)
    print(f"Strategy: {report.strategy_name}")
    print(f"Status: {report.status.value}")
    print(f"Trades: {report.total_trades}")
    print(f"Win Rate: {report.win_rate:.1f}%")
    print(f"Profit Factor: {report.profit_factor:.2f}")
    print(f"Net Profit: ${report.net_profit:.2f}")
    print(f"Maximum Drawdown: {report.maximum_drawdown:.2f}%")
    print(f"Market Conditions Tested:")
    print(f"   Trending: {report.trending_trades}")
    print(f"   Ranging: {report.ranging_trades}")
    print(f"Recommendation: {report.recommendation}")
    print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(run_paper_trading_demo())
