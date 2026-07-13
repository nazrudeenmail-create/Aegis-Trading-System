"""
Market Session Manager

Responsible for determining the current trading session state for a given instrument
based on its exchange and current time. Queries the `market_sessions` and `market_holidays`
tables built in Phase 2. Emits SessionEvent updates if the state changes.
"""
from datetime import datetime, timezone
from enum import Enum
import logging
from sqlalchemy import select

from app.database.enums import MarketType
from app.analytics.events import EventBus
from app.database.connection import SessionLocal
from app.database.models.market_session import MarketSession
from app.database.models.market_holiday import MarketHoliday

logger = logging.getLogger(__name__)

class MarketSessionState(str, Enum):
    """Rich internal session states for an instrument."""
    PRE_MARKET = "PRE_MARKET"
    REGULAR = "REGULAR"
    EXTENDED = "EXTENDED"
    POST_MARKET = "POST_MARKET"
    HOLIDAY = "HOLIDAY"
    WEEKEND = "WEEKEND"
    AFTER_HOURS_CLOSED = "AFTER_HOURS_CLOSED"
    CLOSED = "CLOSED"  # Generic fallback


class SessionManager:
    """Evaluates instrument market types and exchange schedules to determine current trading sessions."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._last_states: dict[int, MarketSessionState] = {}
        
    def get_current_session_state(self, market_type: MarketType, exchange: str = "DEFAULT", current_time: datetime | None = None) -> MarketSessionState:
        """Determines the session state based on the market type and database rules."""
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        # Crypto is always 24/7
        if market_type == MarketType.CRYPTO:
            return MarketSessionState.REGULAR
            
        day_of_week = current_time.weekday() # 0 = Monday, 6 = Sunday
        
        # Check database for holidays
        with SessionLocal() as db:
            holiday = db.execute(
                select(MarketHoliday).where(
                    MarketHoliday.exchange == exchange,
                    MarketHoliday.holiday_date == current_time.date()
                )
            ).scalar_one_or_none()
            
            if holiday:
                return MarketSessionState.HOLIDAY
                
            # Check database for session rules
            session_rule = db.execute(
                select(MarketSession).where(
                    MarketSession.exchange == exchange,
                    MarketSession.day_of_week == day_of_week,
                    MarketSession.is_active == True
                )
            ).scalar_one_or_none()
            
            if not session_rule:
                # If no explicit rule, and it's weekend, assume closed.
                if day_of_week >= 5:
                    return MarketSessionState.WEEKEND
                # No rule but weekday — assume open (fallback for unconfigured exchanges)
                return MarketSessionState.REGULAR
                
            # Convert current UTC time to a simple time object to compare with DB
            # We assume open_time and close_time in DB are normalized to UTC for simplicity here
            current_time_only = current_time.time()
            
            if session_rule.open_time <= current_time_only <= session_rule.close_time:
                return MarketSessionState.REGULAR
            
            # Simplified pre/post market checks
            return MarketSessionState.CLOSED
            
    def update_instrument_session(self, instrument_id: int, market_type: MarketType, exchange: str = "DEFAULT") -> MarketSessionState:
        """Checks the session and emits an event if it changed."""
        current_state = self.get_current_session_state(market_type, exchange)
        
        last_state = self._last_states.get(instrument_id)
        if last_state != current_state:
            self._last_states[instrument_id] = current_state
            logger.info(f"Instrument {instrument_id} session changed: {last_state} -> {current_state}")
            
            # Emit event to the EventBus so WebSocket can broadcast it
            self.event_bus.publish({
                "type": "SESSION_CHANGED",
                "instrument_id": instrument_id,
                "old_state": last_state,
                "new_state": current_state,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        return current_state

    def is_market_open(self, market_type: MarketType, exchange: str = "DEFAULT") -> bool:
        """Helper to quickly check if the market is open for pipeline gatekeeping."""
        state = self.get_current_session_state(market_type, exchange)
        return state in [MarketSessionState.REGULAR, MarketSessionState.EXTENDED]
