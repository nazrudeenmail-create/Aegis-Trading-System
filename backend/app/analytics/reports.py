"""
Aegis Trading System - Analytics Reports
"""

from typing import List
from datetime import datetime
from decimal import Decimal

from app.analytics.models import DecisionRecord, StrategyIntelligenceReport
from app.analytics.performance import AnalyticsEngine


class ReportGenerator:
    """
    Generates the Strategy Intelligence Report from a list of DecisionRecords.
    """
    
    @staticmethod
    def generate_intelligence_report(decisions: List[DecisionRecord]) -> StrategyIntelligenceReport:
        strategy_perf = AnalyticsEngine.calculate_strategy_performance(decisions)
        regime_perf = AnalyticsEngine.calculate_regime_performance(decisions)
        ranking_acc = AnalyticsEngine.calculate_ranking_accuracy(decisions)
        conf_cal = AnalyticsEngine.calculate_confidence_calibration(decisions)
        
        executed_trades = [d for d in decisions if d.outcome_status in ["WIN", "LOSS", "BREAK_EVEN"]]
        total_pnl = sum([d.profit_loss for d in executed_trades if d.profit_loss], Decimal("0"))
        
        return StrategyIntelligenceReport(
            generated_at=datetime.now(),
            total_decisions_logged=len(decisions),
            total_trades_executed=len(executed_trades),
            overall_net_profit=total_pnl,
            strategy_performance=strategy_perf,
            regime_performance=regime_perf,
            ranking_accuracy=ranking_acc,
            confidence_calibration=conf_cal
        )
