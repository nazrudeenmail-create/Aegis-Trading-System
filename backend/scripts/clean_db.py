import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings
from app.database.models import Base

async def clean_db():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    
    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Recreating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Seeding default user...")
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO users (username, email, hashed_password, api_key_hash, role, is_active)
            VALUES ('admin', 'admin@example.com', 'hashed', 'dev-secret-key', 'ADMIN', true)
        """))
        
    print("Database cleaned and recreated.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(clean_db())
