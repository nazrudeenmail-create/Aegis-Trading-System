import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models import BacktestRun

class HistoricalScorer:
    """
    Computes the Historical Performance Score (0-100) for a strategy based on its best recent BacktestRun.
    """
    def __init__(self, db: Session):
        self.db = db

    def score(self, strategy_name: str) -> float:
        # Get the latest backtest run for this strategy
        run = self.db.query(BacktestRun).filter(
            BacktestRun.strategy_name == strategy_name
        ).order_by(desc(BacktestRun.end_date)).first()

        if not run or run.total_trades == 0:
            return 0.0

        # 1. Normalize Base Metrics (0-100)
        # Expectancy: Assume a highly profitable system returns 5.0 R-multiple or $500 on standard risk.
        # This is a simplistic cap for absolute values.
        norm_expectancy = min(100.0, max(0.0, float(run.expectancy) * 20.0)) 
        
        # Profit Factor: 1.0 = 0 points, 2.0+ = 100 points
        pf = float(run.profit_factor)
        norm_pf = min(100.0, max(0.0, (pf - 1.0) * 100.0))
        
        # Win Rate: 0 to 100 directly (assuming it's stored as 0.0 - 100.0)
        norm_win_rate = float(run.win_rate)
        
        # Max Drawdown: Lower is better. 0% = 100 points, 20%+ = 0 points
        dd = float(run.max_drawdown)
        norm_dd = max(0.0, 100.0 - (dd * 5.0))

        # 2. Base Score (40/25/20/15 weighting)
        base_score = (
            (norm_expectancy * 0.40) +
            (norm_pf * 0.25) +
            (norm_dd * 0.20) +
            (norm_win_rate * 0.15)
        )

        # 3. Sample Size Protection
        # log10(total_trades) / 3  (10 trades = 0.33, 100 = 0.66, 1000 = 1.0)
        sample_confidence = min(1.0, math.log10(max(1, run.total_trades)) / 3.0)

        # 4. Recency Decay
        # Recent: 1.0, 1 year old: 0.8, 3+ years old: 0.5
        run_end = run.end_date
        if run_end.tzinfo is None:
            run_end = run_end.replace(tzinfo=timezone.utc)
            
        age_days = (datetime.now(timezone.utc) - run_end).days
        
        if age_days <= 365:
            # Linear decay from 1.0 to 0.8 over 1 year
            recency_factor = 1.0 - (0.2 * (age_days / 365.0))
        elif age_days <= 1095: # 3 years
            # Linear decay from 0.8 to 0.5 over next 2 years
            recency_factor = 0.8 - (0.3 * ((age_days - 365) / 730.0))
        else:
            recency_factor = 0.5

        # Final Historical Score
        final_score = base_score * sample_confidence * recency_factor
        return float(max(0.0, final_score))
