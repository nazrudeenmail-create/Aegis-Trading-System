import os
import sys
from decimal import Decimal

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import Instrument
from app.database.enums import AssetClass, InstrumentStatus, MarketType, ExecutionMode

def seed_instruments():
    print("--- Seeding Instruments ---")
    
    # Common demo instruments
    instruments = [
        {
            "symbol": "BTCUSDT",
            "name": "Bitcoin / US Dollar",
            "asset_class": AssetClass.CRYPTO,
            "exchange": "CAPITAL",
            "tick_size": Decimal("0.01"),
            "contract_size": Decimal("1.0"),
            "currency": "USD",
            "status": InstrumentStatus.ACTIVE,
            "market_type": MarketType.CRYPTO,
            "trading_enabled": True,
            "execution_mode": ExecutionMode.DEMO,
            "live_trading_enabled": False,
            "allow_new_positions": True,
        },
        {
            "symbol": "EURUSD",
            "name": "Euro / US Dollar",
            "asset_class": AssetClass.FOREX,
            "exchange": "CAPITAL",
            "tick_size": Decimal("0.00001"),
            "contract_size": Decimal("100000.0"),
            "currency": "USD",
            "status": InstrumentStatus.ACTIVE,
            "market_type": MarketType.FOREX,
            "trading_enabled": True,
            "execution_mode": ExecutionMode.DEMO,
            "live_trading_enabled": False,
            "allow_new_positions": True,
        },
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "asset_class": AssetClass.STOCK,
            "exchange": "CAPITAL",
            "tick_size": Decimal("0.01"),
            "contract_size": Decimal("1.0"),
            "currency": "USD",
            "status": InstrumentStatus.ACTIVE,
            "market_type": MarketType.US_STOCK,
            "trading_enabled": True,
            "execution_mode": ExecutionMode.DEMO,
            "live_trading_enabled": False,
            "allow_new_positions": True,
        }
    ]

    with SessionLocal() as db:
        for data in instruments:
            existing = db.query(Instrument).filter_by(symbol=data["symbol"]).first()
            if existing:
                print(f"[{data['symbol']}] already exists. Skipping.")
            else:
                instrument = Instrument(**data)
                db.add(instrument)
                print(f"[{data['symbol']}] added to seed list.")
        
        db.commit()
        print("✅ Instruments seeded successfully.")

if __name__ == "__main__":
    seed_instruments()
