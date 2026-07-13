import os
import sys

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import Setting
from app.database.enums import SettingValueType

def seed_settings():
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
            "description": "Default risk percentage per trade (e.g., 1.0 = 1%).",
            "category": "risk",
        }
    ]

    with SessionLocal() as db:
        for data in settings_data:
            existing = db.query(Setting).filter_by(key=data["key"]).first()
            if existing:
                print(f"[{data['key']}] already exists. Skipping.")
            else:
                setting = Setting(**data)
                db.add(setting)
                print(f"[{data['key']}] added to seed list.")
        
        db.commit()
        print("✅ Settings seeded successfully.")

if __name__ == "__main__":
    seed_settings()
