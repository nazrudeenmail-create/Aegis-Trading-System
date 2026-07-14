import sys
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add backend dir to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.database.models import IndicatorState, Candle, Instrument
from sqlalchemy import select

def seed_indicators():
    db = SessionLocal()
    
    # Clear old state
    db.query(IndicatorState).delete()

    instruments = db.query(Instrument).all()
    
    for instrument in instruments:
        # Get latest 1M candle to anchor the EMAs near reality
        latest_candle = db.query(Candle).filter(Candle.instrument_id == instrument.id).order_by(Candle.timestamp.desc()).first()
        
        if not latest_candle:
            continue
            
        base_price = latest_candle.close
        timestamp = latest_candle.timestamp - timedelta(minutes=1) # Treat as the "closed" candle time
        
        # We want to create a Bullish alignment to test the EMA Trend Pullback strategy:
        # EMA20 > EMA50 > EMA200
        
        states = [
            # Daily
            IndicatorState(instrument_id=instrument.id, timeframe="D1", indicator_name="EMA20", value=base_price * Decimal("0.99"), candle_time=timestamp),
            IndicatorState(instrument_id=instrument.id, timeframe="D1", indicator_name="EMA50", value=base_price * Decimal("0.98"), candle_time=timestamp),
            IndicatorState(instrument_id=instrument.id, timeframe="D1", indicator_name="EMA200", value=base_price * Decimal("0.95"), candle_time=timestamp),
            
            # H4
            IndicatorState(instrument_id=instrument.id, timeframe="H4", indicator_name="EMA20", value=base_price * Decimal("0.995"), candle_time=timestamp),
            IndicatorState(instrument_id=instrument.id, timeframe="H4", indicator_name="EMA50", value=base_price * Decimal("0.985"), candle_time=timestamp),
            IndicatorState(instrument_id=instrument.id, timeframe="H4", indicator_name="EMA200", value=base_price * Decimal("0.96"), candle_time=timestamp),
            
            # H1
            IndicatorState(instrument_id=instrument.id, timeframe="H1", indicator_name="EMA20", value=base_price * Decimal("0.998"), candle_time=timestamp),
            IndicatorState(instrument_id=instrument.id, timeframe="H1", indicator_name="EMA50", value=base_price * Decimal("0.99"), candle_time=timestamp),
            IndicatorState(instrument_id=instrument.id, timeframe="H1", indicator_name="EMA200", value=base_price * Decimal("0.97"), candle_time=timestamp),
        ]
        
        db.add_all(states)

    db.commit()
    print("Successfully seeded IndicatorState cache with realistic Bullish EMA alignments!")
    db.close()

if __name__ == "__main__":
    seed_indicators()
