from typing import List, Dict
from decimal import Decimal

from app.backtest.simulated_broker import SimulatedTrade

class BacktestStatistics:
    """
    Computes performance metrics from a list of completed simulated trades.
    """
    def __init__(self, initial_balance: Decimal, trades: List[SimulatedTrade]):
        self.initial_balance = initial_balance
        self.trades = trades
        
    def calculate(self) -> Dict[str, Decimal]:
        if not self.trades:
            return {
                "total_trades": Decimal("0"),
                "win_rate": Decimal("0.0"),
                "profit_factor": Decimal("0.0"),
                "expectancy": Decimal("0.0"),
                "max_drawdown": Decimal("0.0"),
                "final_balance": self.initial_balance
            }
            
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        
        total_trades = len(self.trades)
        
        # 1. Win Rate
        win_rate = Decimal(len(winning_trades)) / Decimal(total_trades)
        loss_rate = Decimal(1.0) - win_rate
        
        # 2. Profit Factor
        gross_profit = sum([t.pnl for t in winning_trades]) or Decimal("0.0")
        gross_loss = abs(sum([t.pnl for t in losing_trades])) or Decimal("0.0")
        
        if gross_loss == Decimal("0.0"):
            profit_factor = Decimal("999.0") if gross_profit > 0 else Decimal("0.0")
        else:
            profit_factor = gross_profit / gross_loss
            
        # 3. Expectancy
        avg_win = (gross_profit / len(winning_trades)) if winning_trades else Decimal("0.0")
        avg_loss = (gross_loss / len(losing_trades)) if losing_trades else Decimal("0.0")
        
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        
        # 4. Max Drawdown
        running_balance = self.initial_balance
        peak_balance = self.initial_balance
        max_drawdown_percent = Decimal("0.0")
        
        for trade in self.trades:
            running_balance += trade.pnl
            running_balance -= trade.commission
            
            if running_balance > peak_balance:
                peak_balance = running_balance
                
            drawdown = peak_balance - running_balance
            drawdown_percent = (drawdown / peak_balance) * Decimal("100.0")
            
            if drawdown_percent > max_drawdown_percent:
                max_drawdown_percent = drawdown_percent
                
        final_balance = running_balance
        
        return {
            "total_trades": Decimal(total_trades),
            "win_rate": win_rate * Decimal("100.0"),
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "max_drawdown": max_drawdown_percent,
            "final_balance": final_balance
        }
