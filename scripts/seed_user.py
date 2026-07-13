import os
import sys
import secrets
from datetime import datetime, timezone

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import User
from app.database.enums import UserRole

def seed_user():
    print("--- Seeding Admin User ---")
    
    with SessionLocal() as db:
        existing = db.query(User).filter_by(username="admin").first()
        if existing:
            print("[admin] user already exists. Skipping.")
            return

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
        
        print("✅ Admin user seeded successfully.")
        print("-------------------------------------------------")
        print(f"Username: admin")
        print(f"API Key: ats_{key_prefix}_{secret}")
        print("SAVE THIS KEY! It will not be shown again.")
        print("-------------------------------------------------")

if __name__ == "__main__":
    seed_user()
