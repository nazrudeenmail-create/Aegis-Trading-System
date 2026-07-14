import sys
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add backend dir to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.database.models import BacktestRun, Account
from app.database.enums import AccountType

def seed_backtests():
    db = SessionLocal()
    
    # Clear old runs
    db.query(BacktestRun).delete()
    db.query(Account).filter(Account.account_number.like("BACKTEST_%")).delete(synchronize_session=False)

    now = datetime.now(timezone.utc)
    one_year_ago = now - timedelta(days=365)

    def create_account(num):
        a = Account(
            broker_name="Backtest",
            account_number=num,
            account_type=AccountType.BACKTEST,
            balance=Decimal("10000.00"),
            currency="USD"
        )
        db.add(a)
        db.flush()
        return a

    acc1 = create_account("BACKTEST_EMA_001")
    acc2 = create_account("BACKTEST_DONCHIAN_001")

    runs = [
        BacktestRun(
            account_id=acc1.id,
            strategy_name="EMA Trend Pullback",
            strategy_version="1.0",
            start_date=one_year_ago,
            end_date=now,
            initial_balance=Decimal("10000.00"),
            total_trades=145,
            win_rate=Decimal("54.2"),
            profit_factor=Decimal("1.85"),
            expectancy=Decimal("15.4"),
            max_drawdown=Decimal("8.4"),
            final_balance=Decimal("12230.50")
        ),
        BacktestRun(
            account_id=acc2.id,
            strategy_name="Donchian Channel Breakout",
            strategy_version="1.0",
            start_date=one_year_ago,
            end_date=now,
            initial_balance=Decimal("10000.00"),
            total_trades=82,
            win_rate=Decimal("41.5"),
            profit_factor=Decimal("2.10"),
            expectancy=Decimal("24.1"),
            max_drawdown=Decimal("12.5"),
            final_balance=Decimal("11976.20")
        ),
        BacktestRun(
            account_id=create_account("BACKTEST_MTF_001").id,
            strategy_name="Multi-Timeframe Trend Alignment",
            strategy_version="1.0",
            start_date=one_year_ago,
            end_date=now,
            initial_balance=Decimal("10000.00"),
            total_trades=54,
            win_rate=Decimal("62.5"),
            profit_factor=Decimal("2.40"),
            expectancy=Decimal("31.2"),
            max_drawdown=Decimal("6.5"),
            final_balance=Decimal("13450.00")
        )
    ]

    for run in runs:
        db.add(run)

    db.commit()
    print("Successfully seeded realistic Backtest results into the database!")
    print("The Ranking Engine will now use these for the Historical Score (40%).")
    db.close()

if __name__ == "__main__":
    seed_backtests()
