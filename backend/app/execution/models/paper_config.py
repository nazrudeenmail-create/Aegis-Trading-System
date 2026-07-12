"""
Aegis Trading System - Paper Trading Configuration Models
"""

from decimal import Decimal
from pydantic import BaseModel, Field


class ExecutionSimulationConfig(BaseModel):
    """
    Simulates real market conditions during paper trading.
    """
    slippage_enabled: bool = True
    # Slippage percentage to apply to entry/exit prices (e.g., 0.0005 for 0.05%)
    slippage_percentage: Decimal = Field(default=Decimal("0.0005"))
    
    commission_enabled: bool = True
    # Flat commission fee per trade side (entry and exit)
    commission_rate: Decimal = Field(default=Decimal("1.50"))
    
    # Optional execution delay to mimic network latency
    execution_delay_ms: int = Field(default=100)


class PaperTradingConfig(BaseModel):
    """
    User-configurable rules for validating a strategy in Paper Trading.
    ATS will monitor these rules and notify the user when the strategy is ready.
    """
    enabled: bool = True
    starting_balance: Decimal = Field(default=Decimal("10000.0"))
    
    # Maximum days the paper trading is allowed to run before forced review or timeout
    max_duration_days: int | None = Field(default=None)
    
    # Required number of completed trades before allowing manual live review
    required_trade_count: int | None = Field(default=100)
    
    # Performance thresholds that must be met
    minimum_win_rate: float | None = Field(default=50.0)
    maximum_drawdown: float | None = Field(default=10.0)
    
    # Must always be true. ATS never auto-transitions.
    require_manual_live_approval: bool = True
