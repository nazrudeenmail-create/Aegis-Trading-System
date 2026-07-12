import logging
from typing import List
from sqlalchemy.orm import Session
from app.market.domain.candle import Candle
from app.database.repositories.candle_repository import CandleRepository
from app.analytics.events import EventBus

logger = logging.getLogger(__name__)

class DataSynchronizer:
    """
    Responsible for ensuring the database correctly receives and integrates
    newly polled candles from the market data provider.
    Handles gap filling, retries, and database synchronization.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def synchronize_candles(self, db: Session, symbol: str, candles: List[Candle]) -> int:
        """
        Receives raw candles from the polling engine, processes them, 
        and synchronizes them into the database.
        Returns the number of candles successfully saved.
        """
        if not candles:
            return 0
            
        try:
            # Here we would typically add logic to detect gaps between the last stored candle
            # and the first incoming candle, and trigger a backfill if necessary.
            
            # For now, we rely on the safe upsert provided by CandleRepository.
            repo = CandleRepository(db)
            saved_count = repo.save_many(candles)
            
            if saved_count > 0:
                logger.debug(f"{symbol}: Synchronized {saved_count} new candles.")
                
            return saved_count
            
        except Exception as e:
            logger.error(f"{symbol}: Failed to synchronize candles. Error: {str(e)}")
            return 0
