import asyncio
import sys
import hmac
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_settings

# HMAC key for hashing (must match auth.py)
_HMAC_SECRET = b"ats_internal_hmac_key"

def generate_api_key(key_prefix: str, secret: str) -> str:
    """Generate a full API key with HMAC hash for storage."""
    full_key = f"ats_{key_prefix}_{secret}"
    key_hash = hmac.new(_HMAC_SECRET, full_key.encode(), "sha256").hexdigest()
    return full_key, key_hash


async def seed_user():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(text("SELECT id FROM users WHERE username='admin'"))
        if not result.first():
            # Generate HMAC-based API key
            full_key, key_hash = generate_api_key("dev", "admin-secret-key")
            
            await conn.execute(text(f"""
                INSERT INTO users (username, key_prefix, key_hash, role, is_active, created_at)
                VALUES ('admin', 'ats_dev', '{key_hash}', 'ADMIN', true, NOW())
            """))
            print(f'User seeded. API Key: {full_key}')
        else:
            print('User already exists.')


if sys.platform == 'win32':
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

asyncio.run(seed_user())
