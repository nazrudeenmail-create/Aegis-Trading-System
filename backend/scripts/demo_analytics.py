"""
Aegis Trading System - Phase 10 Analytics Demonstration

Simulates a series of decisions, executions, and trade closures, 
then generates the Strategy Intelligence Report.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import uuid

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analytics.events import event_bus, DecisionEvent, ExecutionEvent, TradeClosedEvent
from app.analytics.journal import DecisionJournal
from app.analytics.reports import ReportGenerator

from app.strategy.models.ranking import RankingResult, StrategyScore
from app.market_analysis.enums import MarketRegime
from app.risk.models import RiskAssessment
from app.execution.models.order import OrderResult, OrderStatus, TradeRecord, OrderDirection


def generate_simulated_activity():
    journal = DecisionJournal(event_bus)
    
    print("--- Simulating Trading Days ---")
    
    # We will simulate 3 decisions:
    # 1. EMA Trend Pullback WIN in Trending
    # 2. Donchian Breakout LOSS in Ranging
    # 3. Rejected trade due to Risk
    
    base_time = datetime.now(timezone.utc) - timedelta(days=5)
    
    # ---------------------------------------------------------
    # Decision 1: EMA Pullback WIN (Trending)
    # ---------------------------------------------------------
    dec1_id = str(uuid.uuid4())
    ord1_id = str(uuid.uuid4())
    
    # Strategy Ranking Engine output
    ranking1 = RankingResult(
        symbol="BTC/USD",
        timeframe="1H",
        timestamp=base_time,
        market_regime=MarketRegime.TRENDING,
        rankings=[
            StrategyScore(strategy_name="EMA Trend Pullback", historical_score=80.0, market_score=90.0, setup_score=85.0, final_score=85.0),
            StrategyScore(strategy_name="Donchian Breakout", historical_score=60.0, market_score=50.0, setup_score=20.0, final_score=43.3)
        ],
        selected_strategy="EMA Trend Pullback",
        selection_reason="Highest final score"
    )
    
    from app.strategy.models import TradeCandidate, TradeDirection
    
    cand1 = TradeCandidate(
        symbol="BTC/USD", strategy_name="EMA Trend Pullback", strategy_version="1.0", direction=TradeDirection.LONG,
        entry_price=Decimal("60000"), stop_loss=Decimal("59000"), take_profit=Decimal("62000"),
        confidence=0.85, market_conditions={"timeframe": "1H", "regime": "trending"}
    )
    risk1 = RiskAssessment(candidate=cand1, is_approved=True, position_size=Decimal("1.5"))
    
    # 1. Emit Decision
    event_bus.publish(DecisionEvent(
        decision_id=dec1_id, symbol="BTC/USD", timeframe="1H",
        ranking_result=ranking1, risk_assessment=risk1
    ))
    
    # 2. Emit Execution
    event_bus.publish(ExecutionEvent(
        decision_id=dec1_id,
        order_result=OrderResult(order_id=ord1_id, status=OrderStatus.FILLED, filled_price=Decimal("60000"), filled_quantity=Decimal("1.5"), timestamp=base_time)
    ))
    
    # 3. Emit Trade Closed (Win)
    event_bus.publish(TradeClosedEvent(
        trade_record=TradeRecord(
            trade_id=ord1_id, symbol="BTC/USD", direction=OrderDirection.LONG,
            entry_price=Decimal("60000"), exit_price=Decimal("62000"), quantity=Decimal("1.5"),
            pnl=Decimal("3000"), pnl_percent=3.33,
            entry_time=base_time, exit_time=base_time + timedelta(hours=2),
            strategy_name="EMA Trend Pullback", ranking_score=Decimal("85.0"), market_regime="trending",
            entry_reason="Ranked top", exit_reason="TAKE_PROFIT"
        )
    ))

    # ---------------------------------------------------------
    # Decision 2: Donchian LOSS (Ranging)
    # ---------------------------------------------------------
    dec2_id = str(uuid.uuid4())
    ord2_id = str(uuid.uuid4())
    
    ranking2 = RankingResult(
        symbol="ETH/USD",
        timeframe="15M",
        timestamp=base_time + timedelta(days=1),
        market_regime=MarketRegime.RANGING,
        rankings=[
            StrategyScore(strategy_name="Donchian Breakout", historical_score=60.0, market_score=80.0, setup_score=95.0, final_score=78.3),
            StrategyScore(strategy_name="EMA Trend Pullback", historical_score=80.0, market_score=30.0, setup_score=10.0, final_score=40.0)
        ],
        selected_strategy="Donchian Breakout",
        selection_reason="Highest final score"
    )
    
    cand2 = TradeCandidate(
        symbol="ETH/USD", strategy_name="Donchian Breakout", strategy_version="1.0", direction=TradeDirection.LONG,
        entry_price=Decimal("3000"), stop_loss=Decimal("2900"), take_profit=Decimal("3300"),
        confidence=0.95, market_conditions={"timeframe": "15M", "regime": "ranging"}
    )
    risk2 = RiskAssessment(candidate=cand2, is_approved=True, position_size=Decimal("2.0"))
    
    event_bus.publish(DecisionEvent(
        decision_id=dec2_id, symbol="ETH/USD", timeframe="15M",
        ranking_result=ranking2, risk_assessment=risk2
    ))
    
    event_bus.publish(ExecutionEvent(
        decision_id=dec2_id,
        order_result=OrderResult(order_id=ord2_id, status=OrderStatus.FILLED, filled_price=Decimal("3000"), filled_quantity=Decimal("2.0"), timestamp=base_time + timedelta(days=1))
    ))
    
    event_bus.publish(TradeClosedEvent(
        trade_record=TradeRecord(
            trade_id=ord2_id, symbol="ETH/USD", direction=OrderDirection.LONG,
            entry_price=Decimal("3000"), exit_price=Decimal("2900"), quantity=Decimal("2.0"),
            pnl=Decimal("-200"), pnl_percent=-3.33,
            entry_time=base_time + timedelta(days=1), exit_time=base_time + timedelta(days=1, hours=1),
            strategy_name="Donchian Breakout", ranking_score=Decimal("78.3"), market_regime="ranging",
            entry_reason="Ranked top", exit_reason="STOP_LOSS"
        )
    ))

    # ---------------------------------------------------------
    # Decision 3: REJECTED by Risk (Trending)
    # ---------------------------------------------------------
    dec3_id = str(uuid.uuid4())
    
    ranking3 = RankingResult(
        symbol="SOL/USD",
        timeframe="1H",
        timestamp=base_time + timedelta(days=2),
        market_regime=MarketRegime.TRENDING,
        rankings=[
            StrategyScore(strategy_name="EMA Trend Pullback", historical_score=80.0, market_score=90.0, setup_score=99.0, final_score=89.6),
        ],
        selected_strategy="EMA Trend Pullback",
        selection_reason="Highest final score"
    )
    
    cand3 = TradeCandidate(
        symbol="SOL/USD", strategy_name="EMA Trend Pullback", strategy_version="1.0", direction=TradeDirection.LONG,
        entry_price=Decimal("150"), stop_loss=Decimal("140"), take_profit=Decimal("170"),
        confidence=0.99, market_conditions={"timeframe": "1H", "regime": "trending"}
    )
    risk3 = RiskAssessment(candidate=cand3, is_approved=False, position_size=Decimal("0"), rejection_reason="Max exposure limits exceeded.")
    
    event_bus.publish(DecisionEvent(
        decision_id=dec3_id, symbol="SOL/USD", timeframe="1H",
        ranking_result=ranking3, risk_assessment=risk3
    ))
    # No ExecutionEvent or TradeClosedEvent since it was rejected
    
    return journal


def print_report(report):
    print("\n========================================================")
    print("             STRATEGY INTELLIGENCE REPORT                 ")
    print("========================================================")
    print(f"Total Decisions Logged: {report.total_decisions_logged}")
    print(f"Total Trades Executed:  {report.total_trades_executed}")
    print(f"Overall Net Profit:     ${report.overall_net_profit}")
    
    print("\n--- Strategy Performance ---")
    for s_name, s_perf in report.strategy_performance.items():
        print(f"\n  Strategy: {s_name}")
        print(f"    Trades: {s_perf.total_trades} ({s_perf.winning_trades}W / {s_perf.losing_trades}L)")
        print(f"    Win Rate: {s_perf.win_rate:.1f}%")
        print(f"    Net PnL: ${s_perf.net_profit}")
        
    print("\n--- Regime Performance ---")
    for r_name, r_perf in report.regime_performance.items():
        print(f"\n  Regime: {r_name.upper()}")
        print(f"    Trades: {r_perf.total_trades} | Win Rate: {r_perf.win_rate:.1f}% | Net PnL: ${r_perf.net_profit}")
        for s_name, sp in r_perf.strategy_breakdown.items():
            print(f"      -> {s_name}: {sp.win_rate:.1f}% Win Rate, ${sp.net_profit}")
            
    print("\n--- System Intelligence ---")
    print(f"  Ranking Accuracy: {report.ranking_accuracy.accuracy_percent:.1f}%")
    print("  Confidence Calibration:")
    for cal in report.confidence_calibration:
        if cal.total_trades > 0:
            print(f"    {cal.confidence_bucket} Bucket: {cal.win_rate:.1f}% Win Rate ({cal.total_trades} trades)")
            
    print("========================================================\n")


if __name__ == "__main__":
    journal = generate_simulated_activity()
    decisions = journal.get_all_decisions()
    
    report = ReportGenerator.generate_intelligence_report(decisions)
    print_report(report)
    
    print("Demo complete. Check output for decision analytics.")
