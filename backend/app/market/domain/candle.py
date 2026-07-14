from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.market.domain.timeframe import Timeframe


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Candle(BaseModel):
    """
    Pure domain model for a Market Candle.
    Isolates the ATS engine from broker-specific API payloads.
    """
    model_config = ConfigDict(frozen=True, from_attributes=True)  # Domain models should be immutable to prevent accidental mutation

    instrument: str = Field(..., description="Instrument symbol, e.g., EURUSD")
    timeframe: Timeframe = Field(..., description="Candle timeframe")
    timestamp: datetime = Field(..., description="Candle start time (UTC)")
    
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: Decimal = Field(..., description="Trading volume")
    
    source: str = Field(..., description="Data source provider, e.g., capital_com")
    created_at: datetime = Field(default_factory=utc_now, description="When this object was created")
