from app.database.connection import SessionLocal
from app.market_analysis.mtf_service import MultiTimeframeService
from app.market.domain.timeframe import Timeframe
from app.database.repositories.candle_repository import CandleRepository
import traceback

def main():
    db = SessionLocal()
    
    # Fetch some candles directly
    repo = CandleRepository(db)
    candles = repo.get_latest("BTCUSD", limit=500)
    
    mtf = MultiTimeframeService()
    try:
        context = mtf.build_context(
            db=db,
            base_1m_candles=candles,
            required_timeframes=[Timeframe.M1, Timeframe.M5, Timeframe.M15, Timeframe.H1, Timeframe.H4, Timeframe.D1],
            primary_timeframe=Timeframe.H4,
        )
        print("Success!")
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
