import os
import sys
import secrets
from decimal import Decimal

# Ensure backend can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import Setting, User, Instrument
from app.database.enums import SettingValueType, UserRole, AssetClass, InstrumentStatus, MarketType, ExecutionMode

def seed_settings(db: Session):
    print("--- Seeding Settings ---")
    settings_data = [
        {
            "key": "SYSTEM_LIVE_TRADING_ENABLED",
            "value": "false",
            "value_type": SettingValueType.BOOLEAN,
            "description": "Master switch for live trading. If false, system stays in DEMO.",
            "category": "system",
        },
        {
            "key": "MAX_OPEN_POSITIONS",
            "value": "5",
            "value_type": SettingValueType.INTEGER,
            "description": "Maximum number of allowed open positions concurrently.",
            "category": "risk",
        },
        {
            "key": "DEFAULT_RISK_PER_TRADE",
            "value": "1.0",
            "value_type": SettingValueType.FLOAT,
            "description": "Default risk percentage per trade.",
            "category": "risk",
        }
    ]
    for data in settings_data:
        if not db.query(Setting).filter_by(key=data["key"]).first():
            db.add(Setting(**data))
            print(f"[{data['key']}] setting added.")
    db.commit()

def seed_user(db: Session):
    print("--- Seeding Admin User ---")
    if not db.query(User).filter_by(username="admin").first():
        key_prefix = secrets.token_hex(4)
        secret = secrets.token_hex(16)
        user = User(
            username="admin",
            key_prefix=key_prefix,
            key_hash=User.hash_secret(secret),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"✅ Admin user seeded.")
        print("-------------------------------------------------")
        print(f"Username: admin")
        print(f"API Key: ats_{key_prefix}_{secret}")
        print("SAVE THIS KEY! It will not be shown again.")
        print("-------------------------------------------------")
    else:
        print("[admin] user already exists.")

def seed_instruments(db: Session):
    print("--- Seeding Demo Instruments ---")
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
    for data in instruments:
        if not db.query(Instrument).filter_by(symbol=data["symbol"]).first():
            db.add(Instrument(**data))
            print(f"[{data['symbol']}] added.")
    db.commit()

def main():
    print("==================================================")
    print("Running ATS Automatic Database Seed")
    print("==================================================")
    with SessionLocal() as db:
        seed_settings(db)
        seed_user(db)
        seed_instruments(db)
    print("✅ All seed data loaded successfully!")

if __name__ == "__main__":
    main()
