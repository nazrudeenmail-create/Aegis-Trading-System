import os
import sys
import json
from datetime import datetime

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import Setting, Instrument

def serialize_model(instance):
    """Convert SQLAlchemy model instance to dict, handling enums and dates."""
    data = {}
    for column in instance.__table__.columns:
        value = getattr(instance, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        elif hasattr(value, 'value'): # Handle enums
            value = value.value
        elif hasattr(value, '__float__'): # Handle decimals
            value = float(value)
        data[column.name] = value
    return data

def export_state(output_file="ats_trading_state.json"):
    print("--- Exporting Trading State ---")
    
    state = {
        "settings": [],
        "instruments": []
    }

    with SessionLocal() as db:
        settings = db.query(Setting).all()
        state["settings"] = [serialize_model(s) for s in settings]
        
        instruments = db.query(Instrument).all()
        state["instruments"] = [serialize_model(i) for i in instruments]
        
    with open(output_file, 'w') as f:
        json.dump(state, f, indent=4)
        
    print(f"✅ Exported {len(state['settings'])} settings and {len(state['instruments'])} instruments to {output_file}")

if __name__ == "__main__":
    export_file = sys.argv[1] if len(sys.argv) > 1 else "ats_trading_state.json"
    export_state(export_file)
