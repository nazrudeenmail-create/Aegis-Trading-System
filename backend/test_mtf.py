from app.database.connection import SessionLocal
from app.workers.orchestrator import Orchestrator
db = SessionLocal()
orc = Orchestrator()
orc._fetch_recent_candles(db, "BTCUSD")
candles = orc._fetch_recent_candles(db, "BTCUSD")
from app.market.domain.timeframe import Timeframe
try:
    context = orc.market_service.build_context(
        db=db,
        base_1m_candles=candles,
        required_timeframes=[Timeframe.M1],
        primary_timeframe=Timeframe.H4,
    )
except Exception as e:
    import traceback
    traceback.print_exc()
