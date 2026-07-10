from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Instrument(BaseModel):
    """
    Pure domain model for a Market Instrument.
    """
    model_config = ConfigDict(frozen=True)
    
    symbol: str = Field(..., description="Unique trading symbol, e.g., EURUSD")
    name: str = Field(..., description="Human readable name")
    asset_class: str = Field(..., description="Asset class, e.g., FOREX, CRYPTO")
    exchange: str = Field(..., description="Exchange name")
    tick_size: Decimal = Field(..., description="Minimum price movement")
    contract_size: Decimal = Field(default=Decimal("1.0"), description="Contract multiplier")
    currency: str = Field(..., description="Quote currency")
