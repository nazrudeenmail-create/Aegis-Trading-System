import os
import sys
import json
from datetime import datetime
from decimal import Decimal

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.database.connection import SessionLocal
from app.database.models import Setting, Instrument

def deserialize_dict(data, model_class):
    """Convert JSON dict values to appropriate types for the model."""
    clean_data = {}
    for col in model_class.__table__.columns:
        if col.name in data:
            val = data[col.name]
            # Convert ISO datetime strings back to datetime objects
            if val is not None and str(col.type) == 'DATETIME' or 'TIMESTAMP' in str(col.type):
                if isinstance(val, str):
                    try:
                        val = datetime.fromisoformat(val)
                    except ValueError:
                        pass
            clean_data[col.name] = val
    return clean_data

def import_state(input_file="ats_trading_state.json"):
    print("--- Importing Trading State ---")
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
        
    with open(input_file, 'r') as f:
        state = json.load(f)

    with SessionLocal() as db:
        # Import Settings
        for setting_data in state.get("settings", []):
            clean_data = deserialize_dict(setting_data, Setting)
            stmt = insert(Setting).values(**clean_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['key'],
                set_={k: v for k, v in clean_data.items() if k not in ['id', 'key', 'created_at']}
            )
            db.execute(stmt)
            
        # Import Instruments
        for inst_data in state.get("instruments", []):
            clean_data = deserialize_dict(inst_data, Instrument)
            stmt = insert(Instrument).values(**clean_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['symbol'],
                set_={k: v for k, v in clean_data.items() if k not in ['id', 'symbol', 'created_at']}
            )
            db.execute(stmt)
            
        db.commit()
        
    print(f"✅ State successfully imported from {input_file}")

if __name__ == "__main__":
    import_file = sys.argv[1] if len(sys.argv) > 1 else "ats_trading_state.json"
    import_state(import_file)
