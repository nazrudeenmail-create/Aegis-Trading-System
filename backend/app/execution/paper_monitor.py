"""
Aegis Trading System - Paper Trading Monitor
"""

from decimal import Decimal
from typing import List

from app.execution.models.paper_config import PaperTradingConfig
from app.execution.models.validation_report import ValidationReport, PaperTradingStatus
from app.execution.models.order import TradeRecord


class PaperTradingMonitor:
    """
    Monitors paper trading execution results.
    Generates validation reports and determines if a strategy is ready for live review.
    """
    
    def __init__(self, config: PaperTradingConfig):
        self.config = config

    def generate_report(self, strategy_name: str, trades: List[TradeRecord], days_running: int) -> ValidationReport:
        """
        Process the trade records for a specific strategy and generate its validation report.
        """
        # Filter trades for this strategy
        strategy_trades = [t for t in trades if t.strategy_name == strategy_name]
        
        total_trades = len(strategy_trades)
        winning_trades = [t for t in strategy_trades if t.pnl > 0]
        losing_trades = [t for t in strategy_trades if t.pnl <= 0]
        
        # Calculate Win Rate
        win_rate = 0.0
        if total_trades > 0:
            win_rate = (len(winning_trades) / total_trades) * 100.0
            
        # Calculate Profit Factor
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = 0.0
        if gross_loss > 0:
            profit_factor = float(gross_profit / gross_loss)
        elif gross_profit > 0:
            profit_factor = 999.9  # Arbitrary high number if no losses
            
        # Calculate Average R
        # MVP: simplified Average R (Average Win / Average Loss)
        avg_win = gross_profit / len(winning_trades) if winning_trades else Decimal("0")
        avg_loss = gross_loss / len(losing_trades) if losing_trades else Decimal("0")
        average_r = 0.0
        if avg_loss > 0:
            average_r = float(avg_win / avg_loss)
            
        # Calculate Max Drawdown (Simplified based on PnL curve)
        max_drawdown = 0.0
        peak = Decimal("0")
        current_equity = Decimal("0")
        for t in strategy_trades:
            current_equity += t.pnl
            if current_equity > peak:
                peak = current_equity
            drawdown = peak - current_equity
            # Avoid division by zero by assuming an arbitrary initial balance for % calculation
            # Or use absolute drawdown. Let's return percentage of starting balance.
            dd_percent = float(drawdown / self.config.starting_balance) * 100.0
            if dd_percent > max_drawdown:
                max_drawdown = dd_percent
                
        net_profit = sum(t.pnl for t in strategy_trades)
        
        # Determine Market Behavior Distribution
        trending = len([t for t in strategy_trades if t.market_regime == "TRENDING"])
        ranging = len([t for t in strategy_trades if t.market_regime == "RANGING"])
        breakout = len([t for t in strategy_trades if t.market_regime == "BREAKOUT"])
        capitulation = len([t for t in strategy_trades if t.market_regime == "CAPITULATION"])
        
        # Validation Logic
        status = PaperTradingStatus.ACTIVE
        recommendation = "Gathering more data."
        
        if not self.config.enabled:
            status = PaperTradingStatus.FAILED_VALIDATION
            recommendation = "Paper trading is disabled."
        elif self.config.max_duration_days and days_running >= self.config.max_duration_days:
            # Reached max days
            if self._meets_thresholds(total_trades, win_rate, max_drawdown):
                status = PaperTradingStatus.READY_FOR_REVIEW
                recommendation = "Max duration reached. Thresholds met. Ready for manual review."
            else:
                status = PaperTradingStatus.FAILED_VALIDATION
                recommendation = "Max duration reached. Failed to meet performance thresholds."
        elif self._meets_thresholds(total_trades, win_rate, max_drawdown):
            status = PaperTradingStatus.READY_FOR_REVIEW
            recommendation = "Target thresholds met. Ready for manual review."
            
        return ValidationReport(
            strategy_name=strategy_name,
            status=status,
            days_running=days_running,
            total_trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            average_r=average_r,
            maximum_drawdown=max_drawdown,
            net_profit=net_profit,
            rejected_orders=0, # Tracked separately by the engine in a full system
            risk_violations=0,
            execution_errors=0,
            trending_trades=trending,
            ranging_trades=ranging,
            breakout_trades=breakout,
            capitulation_trades=capitulation,
            recommendation=recommendation
        )
        
    def _meets_thresholds(self, total_trades: int, win_rate: float, max_drawdown: float) -> bool:
        if self.config.required_trade_count and total_trades < self.config.required_trade_count:
            return False
        if self.config.minimum_win_rate and win_rate < self.config.minimum_win_rate:
            return False
        if self.config.maximum_drawdown and max_drawdown > self.config.maximum_drawdown:
            return False
        return True
