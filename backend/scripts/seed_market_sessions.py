"""
Seed market_sessions table with default trading hours for the CAPITAL exchange.

Capital.com offers near-24/5 trading for commodities/forex.
Run this after migrations to ensure the SessionManager can determine market state.

Usage:
    python -m scripts.seed_market_sessions
"""
from datetime import time

from app.database.connection import SessionLocal
from app.database.models.market_session import MarketSession


def seed_market_sessions():
    """Seed default CAPITAL exchange session rules (Mon-Fri, near 24h UTC)."""
    db = SessionLocal()
    try:
        existing = db.query(MarketSession).filter_by(exchange="CAPITAL").count()
        if existing > 0:
            print(f"market_sessions already seeded ({existing} rows for CAPITAL). Skipping.")
            return

        sessions = [
            MarketSession(exchange="CAPITAL", day_of_week=0, open_time=time(0, 0), close_time=time(23, 59), timezone="UTC", is_active=True),  # Monday
            MarketSession(exchange="CAPITAL", day_of_week=1, open_time=time(0, 0), close_time=time(23, 59), timezone="UTC", is_active=True),  # Tuesday
            MarketSession(exchange="CAPITAL", day_of_week=2, open_time=time(0, 0), close_time=time(23, 59), timezone="UTC", is_active=True),  # Wednesday
            MarketSession(exchange="CAPITAL", day_of_week=3, open_time=time(0, 0), close_time=time(23, 59), timezone="UTC", is_active=True),  # Thursday
            MarketSession(exchange="CAPITAL", day_of_week=4, open_time=time(0, 0), close_time=time(22, 0), timezone="UTC", is_active=True),   # Friday (closes 22:00)
        ]

        for s in sessions:
            db.add(s)

        db.commit()
        print(f"Seeded {len(sessions)} market_sessions for CAPITAL exchange (Mon-Fri)")
    except Exception as e:
        db.rollback()
        print(f"Error seeding market_sessions: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_market_sessions()