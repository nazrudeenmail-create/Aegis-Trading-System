import asyncio
import logging
import traceback
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models.instrument import Instrument
from app.database.enums import InstrumentStatus
from app.market.provider_base import MarketDataProvider
from app.market.synchronizer import DataSynchronizer
from app.market.domain.timeframe import Timeframe
from app.analytics.events import EventBus

logger = logging.getLogger(__name__)

class MarketDataEngine:
    """
    Dedicated background engine responsible for live data polling.
    Runs independently of the analysis orchestrator to prevent network IO 
    from blocking trading intelligence pipelines.
    """
    
    def __init__(
        self, 
        event_bus: EventBus,
        provider: MarketDataProvider,
        synchronizer: DataSynchronizer,
        poll_interval_seconds: int = 60
    ):
        self.event_bus = event_bus
        self.provider = provider
        self.synchronizer = synchronizer
        self.poll_interval_seconds = poll_interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(f"MarketDataEngine started (interval={self.poll_interval_seconds}s).")
        
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("MarketDataEngine stopped.")
        
    async def _poll_loop(self):
        while self._running:
            try:
                await self._poll_all_instruments()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"MarketDataEngine poll loop error: {str(e)}")
                logger.error(traceback.format_exc())
                
            # Sleep until next interval
            await asyncio.sleep(self.poll_interval_seconds)
            
    async def _poll_all_instruments(self):
        # We use a fresh short-lived DB session for each poll iteration
        db: Session = SessionLocal()
        try:
            # We want to poll data for any instrument that is ACTIVE or WATCHLIST
            result = db.execute(
                select(Instrument).where(
                    Instrument.status.in_([InstrumentStatus.ACTIVE, InstrumentStatus.WATCHLIST])
                )
            )
            instruments = result.scalars().all()
            
            if not instruments:
                return
                
            # Authenticate provider if needed before making many requests
            try:
                self.provider.authenticate()
            except Exception as e:
                logger.error(f"MarketDataEngine failed to authenticate provider: {e}")
                return
                
            for instrument in instruments:
                if not self._running:
                    break
                    
                await self._fetch_and_sync(db, instrument.symbol)
                
        finally:
            db.close()
            
    async def _fetch_and_sync(self, db: Session, symbol: str):
        try:
            # For live polling, fetching the last 5-10 candles is enough to catch up
            # if we missed a minute or two.
            # CapitalComProvider is synchronous right now, so we run it in a thread
            # if it blocks too much, but for now we just call it.
            # In a production system we'd use run_in_executor for sync requests
            candles = await asyncio.to_thread(
                self.provider.fetch_historical_candles,
                instrument=symbol,
                timeframe=Timeframe.M1,
                limit=10
            )
            
            # Use Synchronizer to handle gap fills, retries, and DB persistence
            saved = self.synchronizer.synchronize_candles(db, symbol, candles)
            if saved > 0:
                logger.debug(f"MarketDataEngine: {symbol} synchronized {saved} new live candles.")
                
        except Exception as e:
            logger.error(f"MarketDataEngine failed to fetch live data for {symbol}: {e}")
