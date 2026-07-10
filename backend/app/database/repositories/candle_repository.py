from typing import List
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.models.candle import Candle as CandleModel
from app.database.models.instrument import Instrument as InstrumentModel
from app.market.domain.candle import Candle as DomainCandle
from app.market.domain.timeframe import Timeframe

logger = logging.getLogger(__name__)


class CandleRepository:
    """
    Repository for Candle database operations.
    Accepts and returns pure Domain objects, isolating the rest of ATS from SQLAlchemy.
    Strictly stores and retrieves only 1M raw truth candles.
    """

    def __init__(self, session: Session):
        self.session = session

    def save_many(self, candles: List[DomainCandle]) -> int:
        """
        Saves multiple domain candles to the database.
        Uses PostgreSQL upsert (ON CONFLICT DO NOTHING) to safely handle duplicates.
        Returns the exact number of candles inserted.
        """
        if not candles:
            return 0

        # Fetch instrument IDs to map string symbols to database IDs
        symbols = {c.instrument for c in candles}
        instruments = self.session.execute(
            select(InstrumentModel.id, InstrumentModel.symbol)
            .where(InstrumentModel.symbol.in_(symbols))
        ).all()
        symbol_to_id = {row.symbol: row.id for row in instruments}

        # Prepare records for insertion
        records = []
        for c in candles:
            instrument_id = symbol_to_id.get(c.instrument)
            if not instrument_id:
                # If instrument is missing, we must skip or handle it. 
                logger.warning(f"Skipping candle: Instrument '{c.instrument}' not found in database.")
                continue
            
            records.append({
                "instrument_id": instrument_id,
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            })

        if not records:
            return 0

        # Perform bulk upsert (insert or ignore on conflict)
        stmt = insert(CandleModel).values(records)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["instrument_id", "timestamp"]
        ).returning(CandleModel.id)

        try:
            result = self.session.execute(stmt)
            inserted_count = len(result.all())
            self.session.commit()
            return inserted_count
        except Exception as e:
            self.session.rollback()
            logger.error(f"Transaction failed during save_many. Rolled back. Error: {str(e)}")
            raise

    def get_latest(self, instrument: str, limit: int) -> List[DomainCandle]:
        """
        Retrieves the latest N 1M candles for a specific instrument.
        Returns pure Domain objects.
        """
        stmt = (
            select(CandleModel, InstrumentModel.symbol)
            .join(InstrumentModel)
            .where(InstrumentModel.symbol == instrument)
            .order_by(CandleModel.timestamp.desc())
            .limit(limit)
        )
        
        result = self.session.execute(stmt).all()
        
        domain_candles = []
        for model, symbol in result:
            domain_candles.append(
                DomainCandle(
                    instrument=symbol,
                    timeframe=Timeframe.M1,  # DB only stores 1M truth
                    timestamp=model.timestamp,
                    open=model.open,
                    high=model.high,
                    low=model.low,
                    close=model.close,
                    volume=model.volume,
                    source="database",
                    created_at=model.created_at
                )
            )
            
        # Return in chronological order (oldest first)
        return list(reversed(domain_candles))
