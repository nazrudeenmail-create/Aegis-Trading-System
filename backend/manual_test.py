import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.market.providers.capital_com_provider import CapitalComProvider
from app.database.repositories.candle_repository import CandleRepository
from app.services.data_ingestion_service import DataIngestionService
from app.market.domain.timeframe import Timeframe
from app.database.models.instrument import Instrument
from app.database.models.candle import Candle as CandleModel

def run_test():
    settings = get_settings()
    
    # SAFETY CHECK 1: Confirm Database is Development
    print("="*50)
    print("SAFETY CHECK: Database Connection")
    print(f"DATABASE_URL = {settings.DATABASE_URL}")
    if "production" in settings.DATABASE_URL.lower():
        print("❌ ERROR: Connected to production! Aborting manual test.")
        return
    print("✅ Verified development database.")
    print("="*50)

    # 1. Connect to Database
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # SAFETY CHECK 2: Do NOT auto-create instrument. Require TEST_EURUSD or EURUSD.
        # Check if TEST_EURUSD exists, otherwise check EURUSD.
        test_symbol = "BTCUSD" 
        instrument = db.query(Instrument).filter_by(symbol=test_symbol).first()
        
        if not instrument:
            print(f"❌ ERROR: Instrument '{test_symbol}' not found in database.")
            print("Please run your Phase 2 seeder first, or manually create it.")
            return
            
        print(f"✅ Found instrument: {instrument.symbol}")
        
        # SAFETY CHECK 3: Verify BEFORE counts
        before_count = db.query(CandleModel).count()
        print(f"📊 BEFORE RUN: Total candles in DB = {before_count}")
        
        print("\nConnecting to Capital.com...")
        provider = CapitalComProvider(
            api_url=settings.CAPITAL_COM_API_URL,
            api_key=settings.CAPITAL_COM_API_KEY,
            username=settings.CAPITAL_COM_USERNAME,
            password=settings.CAPITAL_COM_PASSWORD
        )
        
        repo = CandleRepository(db)
        service = DataIngestionService(provider, repo)
        
        # We explicitly request M1 here. (We can refactor the service to hardcode this later!)
        print(f"Fetching 100 M1 candles for {test_symbol}...")
        inserted = service.fetch_and_store_historical(test_symbol, Timeframe.M1, 100)
        
        # SAFETY CHECK 4: Verify AFTER counts
        after_count = db.query(CandleModel).count()
        print(f"\n📊 AFTER RUN: Total candles in DB = {after_count}")
        print(f"📈 Difference: {after_count - before_count} (Expected: {inserted})")
        
        if after_count - before_count == inserted:
            print("✅ SUCCESS! Database count perfectly matches inserted count.")
        else:
            print("⚠️ WARNING: Database count mismatch. Were there duplicate conflicts ignored?")
            
    finally:
        db.close()
        try:
            provider.close()
        except:
            pass

if __name__ == "__main__":
    run_test()
