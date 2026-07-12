from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BacktestConfig(BaseModel):
    """Configuration for a backtest execution."""
    
    strategy_id: str = Field(..., description="Unique ID/name of the strategy to test")
    strategy_version: str = Field(..., description="Version of the strategy")
    
    instrument: str = Field(..., description="Symbol to backtest (e.g. 'EURUSD')")
    
    start_date: datetime = Field(..., description="Start date of the historical replay")
    end_date: datetime = Field(..., description="End date of the historical replay")
    
    initial_balance: Decimal = Field(
        default=Decimal("10000.00"), 
        description="Starting capital"
    )
    
    # Simulation Costs
    commission: Decimal = Field(
        default=Decimal("0.0"), 
        description="Commission per trade/contract"
    )
    spread: Decimal = Field(
        default=Decimal("0.0"), 
        description="Bid/Ask spread to apply to execution price"
    )
    slippage: Decimal = Field(
        default=Decimal("0.0"), 
        description="Execution slippage (in price points/pips)"
    )
