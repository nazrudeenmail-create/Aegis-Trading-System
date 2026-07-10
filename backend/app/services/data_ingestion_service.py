from typing import List
import logging

from app.database.repositories.candle_repository import CandleRepository
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market.provider_base import MarketDataProvider
from app.market.validators.candle_validator import CandleValidator
from app.market.exceptions import MarketDataError

logger = logging.getLogger(__name__)

class DataIngestionService:
    """
    Orchestrates the ingestion of market data.
    Flow: Fetch (Provider) -> Parse -> Validate -> Save (Repository)
    """

    def __init__(self, provider: MarketDataProvider, repository: CandleRepository):
        self.provider = provider
        self.repository = repository

    def fetch_and_store_historical(
        self, instrument: str, timeframe: Timeframe, limit: int = 1000
    ) -> int:
        """
        Fetches historical candles, validates them, and stores them in the database.
        Returns the number of valid candles successfully processed.
        """
        logger.info(f"Fetching {limit} {timeframe.value} candles for {instrument}...")

        try:
            # 1. Fetch & Parse (Handled by Provider)
            candles: List[Candle] = self.provider.fetch_historical_candles(
                instrument=instrument,
                timeframe=timeframe,
                limit=limit
            )

            if not candles:
                logger.warning(f"No candles returned for {instrument} ({timeframe.value}).")
                return 0

            # 2. Validate
            # Provider might return newest first or oldest first.
            # We sort chronologically (oldest first) to run sequence validation.
            candles.sort(key=lambda c: c.timestamp)
            
            CandleValidator.validate_sequence(candles)

            # 3. Save
            inserted_count = self.repository.save_many(candles)
            logger.info(f"Successfully processed and stored {inserted_count} candles.")
            
            return inserted_count

        except MarketDataError as e:
            logger.error(f"Market data ingestion failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during data ingestion: {str(e)}")
            raise
