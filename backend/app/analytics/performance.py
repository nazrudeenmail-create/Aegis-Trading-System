"""
Aegis Trading System - Analytics Performance Engine
"""

from typing import List, Dict
from decimal import Decimal

from app.analytics.models import (
    DecisionRecord,
    StrategyPerformance,
    RegimePerformance,
    ConfidenceCalibration,
    RankingAccuracy
)


class AnalyticsEngine:
    """
    Computes aggregated performance metrics from a history of DecisionRecords.
    """
    
    @staticmethod
    def calculate_strategy_performance(decisions: List[DecisionRecord]) -> Dict[str, StrategyPerformance]:
        stats: Dict[str, StrategyPerformance] = {}
        
        for d in decisions:
            # We only care about executed trades
            if d.outcome_status not in ["WIN", "LOSS", "BREAK_EVEN"]:
                continue
                
            strat = d.selected_strategy
            if not strat:
                continue
                
            if strat not in stats:
                stats[strat] = StrategyPerformance(strategy_name=strat)
                
            perf = stats[strat]
            perf.total_trades += 1
            perf.net_profit += (d.profit_loss or Decimal("0"))
            
            if d.outcome_status == "WIN":
                perf.winning_trades += 1
            elif d.outcome_status == "LOSS":
                perf.losing_trades += 1
                
        # Final pass for derived metrics
        for perf in stats.values():
            if perf.total_trades > 0:
                perf.win_rate = (perf.winning_trades / perf.total_trades) * 100.0
                
            # Expectancy and Profit Factor
            gross_profit = sum([d.profit_loss for d in decisions if d.selected_strategy == perf.strategy_name and d.outcome_status == "WIN" and d.profit_loss], Decimal("0"))
            gross_loss = abs(sum([d.profit_loss for d in decisions if d.selected_strategy == perf.strategy_name and d.outcome_status == "LOSS" and d.profit_loss], Decimal("0")))
            
            if gross_loss > 0:
                perf.profit_factor = float(gross_profit / gross_loss)
            elif gross_profit > 0:
                perf.profit_factor = 999.0 # arbitrary high number for no losses
            else:
                perf.profit_factor = 0.0
                
        return stats

    @staticmethod
    def calculate_regime_performance(decisions: List[DecisionRecord]) -> Dict[str, RegimePerformance]:
        regimes: Dict[str, RegimePerformance] = {}
        
        for d in decisions:
            if d.outcome_status not in ["WIN", "LOSS", "BREAK_EVEN"]:
                continue
                
            regime = d.market_regime
            if regime not in regimes:
                regimes[regime] = RegimePerformance(regime_name=regime)
                
            rp = regimes[regime]
            rp.total_trades += 1
            rp.net_profit += (d.profit_loss or Decimal("0"))
            
            # Update strategy breakdown within regime
            strat = d.selected_strategy
            if strat:
                if strat not in rp.strategy_breakdown:
                    rp.strategy_breakdown[strat] = StrategyPerformance(strategy_name=strat)
                
                sp = rp.strategy_breakdown[strat]
                sp.total_trades += 1
                sp.net_profit += (d.profit_loss or Decimal("0"))
                if d.outcome_status == "WIN":
                    sp.winning_trades += 1
                elif d.outcome_status == "LOSS":
                    sp.losing_trades += 1
                    
        # Final pass
        for rp in regimes.values():
            wins = sum(1 for d in decisions if d.market_regime == rp.regime_name and d.outcome_status == "WIN")
            if rp.total_trades > 0:
                rp.win_rate = (wins / rp.total_trades) * 100.0
                
            for sp in rp.strategy_breakdown.values():
                if sp.total_trades > 0:
                    sp.win_rate = (sp.winning_trades / sp.total_trades) * 100.0
                    
        return regimes

    @staticmethod
    def calculate_ranking_accuracy(decisions: List[DecisionRecord]) -> RankingAccuracy:
        acc = RankingAccuracy()
        
        for d in decisions:
            if d.outcome_status in ["WIN", "LOSS", "BREAK_EVEN"]:
                acc.total_decisions += 1
                # If it made a profit, ranking was accurate in picking a winning setup
                if d.profit_loss and d.profit_loss > 0:
                    acc.profitable_decisions += 1
                    
        if acc.total_decisions > 0:
            acc.accuracy_percent = (acc.profitable_decisions / acc.total_decisions) * 100.0
            
        return acc

    @staticmethod
    def calculate_confidence_calibration(decisions: List[DecisionRecord]) -> List[ConfidenceCalibration]:
        buckets = {
            "0-50%": ConfidenceCalibration(confidence_bucket="0-50%"),
            "51-75%": ConfidenceCalibration(confidence_bucket="51-75%"),
            "76-100%": ConfidenceCalibration(confidence_bucket="76-100%"),
        }
        
        for d in decisions:
            if d.outcome_status not in ["WIN", "LOSS", "BREAK_EVEN"]:
                continue
                
            conf = d.confidence_score or 0.0
            if conf <= 50:
                b = buckets["0-50%"]
            elif conf <= 75:
                b = buckets["51-75%"]
            else:
                b = buckets["76-100%"]
                
            b.total_trades += 1
            if d.outcome_status == "WIN":
                b.win_rate += 1 # we'll store raw wins here and convert below
                
        # Final pass
        for b in buckets.values():
            if b.total_trades > 0:
                b.win_rate = (b.win_rate / b.total_trades) * 100.0
                
        return list(buckets.values())
