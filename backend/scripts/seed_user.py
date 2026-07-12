import asyncio, sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_settings

async def seed_user():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Ignore if username exists using ON CONFLICT DO NOTHING (requires unique constraint)
        # But wait, username is unique constraint. Let's just check if it exists first.
        result = await conn.execute(text("SELECT id FROM users WHERE username='admin'"))
        if not result.first():
            await conn.execute(text("""
                INSERT INTO users (username, api_key_hash, role, is_active, created_at)
                VALUES ('admin', 'dev-secret-key', 'ADMIN', true, NOW())
            """))
            print('User seeded.')
        else:
            print('User already exists.')

if sys.platform == 'win32':
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(seed_user())
