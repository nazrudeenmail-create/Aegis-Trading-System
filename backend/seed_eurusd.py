from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.database.models.instrument import Instrument
from app.database.enums import AssetClass

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

if not db.query(Instrument).filter_by(symbol="EURUSD").first():
    print("Seeding EURUSD...")
    db.add(Instrument(
        symbol="EURUSD",
        name="Euro vs US Dollar",
        asset_class=AssetClass.FOREX,
        exchange="CAPITAL_COM",
        tick_size="0.0001",
        contract_size="1.0",
        currency="USD"
    ))
    db.commit()
    print("EURUSD seeded successfully!")
else:
    print("EURUSD already exists.")
db.close()
