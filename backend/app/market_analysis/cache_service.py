from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session

from app.database.models import IndicatorState
from app.market.domain.candle import Candle
from app.market.domain.timeframe import Timeframe
from app.market_analysis.models import LiveIndicatorContext

from app.database.models.instrument import Instrument

class IndicatorCacheService:
    @staticmethod
    def populate_live_context(db: Session, symbol: str, tf: Timeframe, latest_candle: Candle) -> LiveIndicatorContext:
        """
        Fetches the finalized official IndicatorState (Phase 4.5) for the given timeframe,
        and projects the live estimate for the current unclosed candle.
        """
        context = LiveIndicatorContext()
        
        # Fetch all cached indicators for this instrument and timeframe
        states = db.query(IndicatorState).join(Instrument).filter(
            Instrument.symbol == symbol,
            IndicatorState.timeframe == tf.name
        ).all()
        
        live_price = latest_candle.close
        
        for state in states:
            context.source_candle_time = state.candle_time
            
            if state.indicator_name == "EMA200":
                context.ema_200_closed = state.value
                k = Decimal("2") / (Decimal("200") + 1)
                context.ema_200_live = (live_price * k) + (state.value * (1 - k))
                
            elif state.indicator_name == "EMA50":
                context.ema_50_closed = state.value
                k = Decimal("2") / (Decimal("50") + 1)
                context.ema_50_live = (live_price * k) + (state.value * (1 - k))
                
            elif state.indicator_name == "EMA20":
                context.ema_20_closed = state.value
                k = Decimal("2") / (Decimal("20") + 1)
                context.ema_20_live = (live_price * k) + (state.value * (1 - k))
                
        return context
