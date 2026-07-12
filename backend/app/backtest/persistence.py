import uuid
from decimal import Decimal
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.database.models import Account, BacktestRun, Order, Trade, Position, Instrument
from app.database.enums import AccountType, Direction, OrderStatus, OrderType, PositionStatus
from app.backtest.simulated_broker import SimulatedTrade
from app.backtest.models import BacktestConfig
from app.strategy.models import TradeDirection


class BacktestPersistence:
    """
    Saves a completed backtest execution (and all its simulated orders/positions)
    into the primary database so the Phase 10 Dashboard can read it natively.
    """
    
    @staticmethod
    def save_run(
        db: Session, 
        config: BacktestConfig, 
        closed_trades: List[SimulatedTrade], 
        stats: Dict[str, Any]
    ) -> BacktestRun:
        
        # 1. Fetch Instrument ID
        instrument = db.query(Instrument).filter_by(symbol=config.instrument).first()
        if not instrument:
            # Fallback or strict requirement. For now, create a dummy one if it doesn't exist
            # in test environments, or fail explicitly. We will fail explicitly to enforce integrity.
            raise ValueError(f"Instrument {config.instrument} not found in database.")
            
        # 2. Create Backtest Account
        account = Account(
            name=f"Backtest: {config.strategy_id} v{config.strategy_version}",
            type=AccountType.BACKTEST,
            initial_balance=config.initial_balance,
            current_balance=stats["final_balance"],
            currency="USD"
        )
        db.add(account)
        db.flush()
        
        # 3. Create BacktestRun Metadata
        run = BacktestRun(
            account_id=account.id,
            strategy_name=config.strategy_id,
            strategy_version=config.strategy_version,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_balance=config.initial_balance,
            total_trades=int(stats["total_trades"]),
            win_rate=stats["win_rate"],
            profit_factor=stats["profit_factor"],
            expectancy=stats["expectancy"],
            max_drawdown=stats["max_drawdown"],
            final_balance=stats["final_balance"]
        )
        db.add(run)
        db.flush()
        
        # 4. Save Trades as full DB entities
        for t in closed_trades:
            direction = Direction.LONG if t.position.candidate.direction == TradeDirection.LONG else Direction.SHORT
            
            # Simulated Entry Order
            order = Order(
                instrument_id=instrument.id,
                account_id=account.id,
                client_order_id=str(uuid.uuid4()),
                direction=direction,
                order_type=OrderType.MARKET,
                quantity=t.position.position_size,
                price=t.position.entry_price,
                status=OrderStatus.FILLED,
                filled_price=t.position.entry_price,
                filled_quantity=t.position.position_size,
                submitted_at=t.position.opened_at,
                filled_at=t.position.opened_at
            )
            db.add(order)
            db.flush()
            
            # Simulated Position
            position = Position(
                instrument_id=instrument.id,
                account_id=account.id,
                direction=direction,
                quantity=Decimal("0.0"),  # Final state is closed
                entry_price=t.position.entry_price,
                status=PositionStatus.CLOSED,
                opened_at=t.position.opened_at,
                closed_at=t.closed_at,
                realized_pnl=t.pnl
            )
            db.add(position)
            db.flush()
            
            # Simulated Trade (Round-trip result)
            trade = Trade(
                account_id=account.id,
                instrument_id=instrument.id,
                order_id=order.id,
                position_id=position.id,
                direction=direction, 
                quantity=t.position.position_size,
                price=t.exit_price,
                commission=t.commission,
                realized_pnl=t.pnl,
                executed_at=t.closed_at
            )
            db.add(trade)
            
        db.commit()
        return run
