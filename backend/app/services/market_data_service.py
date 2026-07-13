"""
Market Data Service — Service Layer

Sits between the API layer and the infrastructure layer (BrokerFactory).
The API never touches BrokerFactory directly — it goes through this service.

Architecture:
    API → MarketDataService → BrokerFactory → CapitalComProvider

The provider is injected at construction time for testability.
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.provider_base import MarketDataProvider
from app.database.repositories.candle_repository import CandleRepository

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for market data operations.
    
    Receives a provider instance (injected) rather than calling BrokerFactory
    directly, making it easy to test with mock providers.
    """
    
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider
    
    def fetch_and_store_historical_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int,
        db: Session
    ) -> dict:
        """
        Fetch historical candles from the broker provider and store them in the database.
        
        Args:
            symbol: Instrument symbol (e.g., "EURUSD")
            timeframe: Domain timeframe enum (M1, M5, M15, H1, H4, D1)
            limit: Number of candles to fetch
            db: Database session
            
        Returns:
            dict with status, symbol, candles_fetched, candles_stored
        """
        try:
            self.provider.authenticate()
            candles = self.provider.fetch_historical_candles(
                instrument=symbol,
                timeframe=timeframe,
                limit=limit
            )
            self.provider.close()
            
            if not candles:
                return {
                    "status": "warning",
                    "message": "No candles returned",
                    "count": 0
                }
            
            repo = CandleRepository(db)
            count = repo.save_many(candles)
            
            return {
                "status": "success",
                "symbol": symbol,
                "candles_fetched": len(candles),
                "candles_stored": count
            }
        except Exception as e:
            logger.error(f"MarketDataService: Failed to fetch candles for {symbol}: {e}")
            raise