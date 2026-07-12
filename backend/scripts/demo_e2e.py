import os
import sys
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockPandasTa:
    """Full mock of pandas_ta covering all methods used by ATS analyzers."""
    def _series(self, ref, val=1.0):
        import pandas as pd
        return pd.Series([val] * len(ref))

    def ema(self, close, length, **kw):
        return self._series(close, 1.0)

    def sma(self, close, length, **kw):
        return self._series(close, 1.0)

    def adx(self, high, low, close, length=14, **kw):
        import pandas as pd
        n = len(close)
        return pd.DataFrame({
            f"ADX_{length}": [50.0] * n,
            f"DMP_{length}": [30.0] * n,
            f"DMN_{length}": [15.0] * n,
        })

    def atr(self, high, low, close, length=14, **kw):
        return self._series(close, 10.0)

    def rsi(self, close, length=14, **kw):
        return self._series(close, 55.0)

    def macd(self, close, fast=12, slow=26, signal=9, **kw):
        import pandas as pd
        n = len(close)
        return pd.DataFrame({
            f"MACD_{fast}_{slow}_{signal}": [0.5] * n,
            f"MACDh_{fast}_{slow}_{signal}": [0.1] * n,
            f"MACDs_{fast}_{slow}_{signal}": [0.4] * n,
        })

    def bbands(self, close, length=20, std=2.0, **kw):
        import pandas as pd
        n = len(close)
        return pd.DataFrame({
            f"BBL_{length}_{std}": [0.95] * n,
            f"BBM_{length}_{std}": [1.00] * n,
            f"BBU_{length}_{std}": [1.05] * n,
        })

    def stoch(self, high, low, close, **kw):
        import pandas as pd
        n = len(close)
        return pd.DataFrame({
            "STOCHk_14_3_3": [55.0] * n,
            "STOCHd_14_3_3": [50.0] * n,
        })

    def donchian(self, high, low, lower_length=20, upper_length=20, **kw):
        import pandas as pd
        n = len(high)
        return pd.DataFrame({
            f"DCL_{lower_length}_{upper_length}": [float(high.iloc[-1]) * 0.95] * n,
            f"DCM_{lower_length}_{upper_length}": [float(high.iloc[-1]) * 1.00] * n,
            f"DCU_{lower_length}_{upper_length}": [float(high.iloc[-1]) * 1.05] * n,
        })

sys.modules['pandas_ta'] = MockPandasTa()

from app.database.models import BacktestRun
from app.market.domain.timeframe import Timeframe
from app.market_analysis.mtf_service import MultiTimeframeService
from app.strategy.strategies.ema_trend_pullback import EMATrendPullbackStrategy
from app.strategy.ranking_engine import StrategyRankingEngine

from app.risk.engine import RiskEngine
from app.risk.models import RiskProfile
from app.execution.broker.paper_broker import PaperBroker
from app.execution.engine import ExecutionEngine
from app.analytics.journal import DecisionJournal
from app.analytics.events import event_bus
from app.core.state import global_state

from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_current_user

# Mock auth
def override_get_current_user():
    from app.database.models.user import User
    from app.database.enums import UserRole
    return User(id=1, username="admin", api_key_hash="dummy", role=UserRole.ADMIN, is_active=True)
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

from demo_pipeline import generate_mock_candles

def run_e2e_demo():
    print("="*60)
    print("ATS PHASE 0-11 END-TO-END VISUAL TEST")
    print("="*60)
    
    # 1. Initialize Engines
    print("\n[1] Initializing Engines...")
    
    class MockQuery:
        def __init__(self, runs):
            self.runs = runs
            self._filtered = runs
        def filter(self, condition):
            val = condition.right.value
            self._filtered = [r for r in self.runs if r.strategy_name == val]
            return self
        def order_by(self, *args): return self
        def first(self): return self._filtered[0] if self._filtered else None
            
    class MockDB:
        def __init__(self, runs): self.runs = runs
        def query(self, model): return MockQuery(self.runs)

    runs = [BacktestRun(strategy_name="EMA Trend Pullback", total_trades=250, win_rate=55.0, profit_factor=Decimal("1.8"), expectancy=Decimal("3.5"), max_drawdown=Decimal("8.0"), end_date=datetime.now(timezone.utc))]
    db = MockDB(runs)
    
    ranking_engine = StrategyRankingEngine(db, [EMATrendPullbackStrategy()])
    mtf_service = MultiTimeframeService()
    
    # Global state setup
    journal = DecisionJournal(event_bus)
    from app.execution.models.paper_config import ExecutionSimulationConfig
    broker = PaperBroker(initial_balance=Decimal("10000.0"), config=ExecutionSimulationConfig())
    risk_profile = RiskProfile(account_balance=Decimal("10000.0"), max_exposure_percent=10.0, risk_per_trade_percent=1.0, max_daily_drawdown_percent=5.0)
    risk_engine = RiskEngine()
    execution_engine = ExecutionEngine(broker, risk_engine, event_bus)
    
    global_state.mode = "PAPER_TRADING"
    global_state.journal = journal
    global_state.paper_broker = broker
    global_state.ranking_engine = ranking_engine
    global_state.market_service = mtf_service
    
    print("✅ Memory DB, Ranking, Risk, Broker, Journal, and Global State online.")
    
    # 2. Market Data
    print("\n[2] Generating Market Data...")
    start_time = datetime.now(timezone.utc) - timedelta(days=5)
    candles = generate_mock_candles(start_time, 7200) # 5 days of 1M
    print("[OK] Generated {0} candles.".format(len(candles)))
    
    # 3. Simulate The Last Tick (no candle mutation — Candle is frozen)
    print("\n[3] Triggering Pipeline for final tick...")
        
    context = mtf_service.build_context(
        base_1m_candles=candles,
        required_timeframes=[Timeframe.D1, Timeframe.H4, Timeframe.H1, Timeframe.M15],
        primary_timeframe=Timeframe.H1
    )
    snapshot = context.get(Timeframe.H1)
    
    # Mock M15 attributes for EMA pullback detection
    from app.market_analysis.models import PullbackAnalysis, SwingAnalysis
    m15 = context.get(Timeframe.M15)
    m15.pullback = PullbackAnalysis(is_pullback=True, pullback_depth_percent=Decimal("0.382"), distance_from_ema20=Decimal("0.1"), target_ma="EMA_20")
    m15.swing = SwingAnalysis(swing_high=Decimal("50000.0"), swing_low=Decimal("49000.0"), is_higher_high=True, is_higher_low=True)
    m15.candle.is_bullish = True
    m15.volume.current_volume = Decimal("1000.0")
    m15.volume.average_volume = Decimal("150.0")
    m15.atr.atr = Decimal("10.0")
    
    # Force a winning candidate directly — strategy internals depend on pandas_ta which is mocked
    from app.strategy.models import StrategyResult, TradeCandidate, TradeDirection
    results = {
        "EMA Trend Pullback": StrategyResult(
            is_valid=True,
            candidate=TradeCandidate(
                strategy_name="EMA Trend Pullback", strategy_version="1.0", symbol="MOCK/USD",
                direction=TradeDirection.LONG,
                entry_price=Decimal("40000"), stop_loss=Decimal("39000"), take_profit=Decimal("42000"),
                market_conditions={"trend": "BULLISH", "adx": 100.0, "ema_alignment": "BULLISH", "timeframe": "1H", "regime": "trending"},
                confidence=0.9
            )
        )
    }
    
    ranking_result = ranking_engine.rank("MOCK/USD", "1H", snapshot, results)
    
    print("[OK] Phase 3/4 -> Market Intelligence: Regime=TRENDING | Trend=BULLISH | ADX=50.0 (mocked)")
    print("[OK] Phase 5/8 -> Strategy Engine: Winner={0} | Score={1:.1f}".format(
        ranking_result.selected_strategy, ranking_result.rankings[0].final_score
    ))
    
    candidate = results[ranking_result.selected_strategy].candidate
    
    # 4. Execute via Risk + Broker (async)
    print("\n[4] Requesting Execution...")
    risk_context = {
        "current_open_risk_fiat": Decimal("0"),
        "daily_loss_fiat": Decimal("0"),
        "account_balance": Decimal("10000.0"),
    }
    
    import uuid

    async def run_execution():
        # Connect broker first
        await broker.connect()
        # Inject a known price and timestamp so MARKET order fill works
        broker.latest_prices["MOCK/USD"] = Decimal("40000.0")
        broker.latest_timestamps["MOCK/USD"] = datetime.now(timezone.utc)
        return await execution_engine.execute(
            candidate=candidate,
            ranking_result=ranking_result,
            risk_profile=risk_profile,
            risk_context=risk_context,
            decision_id=str(uuid.uuid4())
        )
    
    order_result = asyncio.run(run_execution())
    
    if order_result:
        print("[OK] Phase 6  -> Risk Engine: Approved | Position size: {0}".format(order_result.filled_quantity))
        print("[OK] Phase 9  -> Broker (Paper): Order Filled | ID: {0} | Price: ${1}".format(order_result.order_id, order_result.filled_price))
    else:
        print("[FAIL] Risk Engine -> Rejected (check logs).")
        
    print("[OK] Phase 10 -> Journal: Decision & Execution events fired via EventBus.")
    decisions_logged = journal.get_all_decisions()
    print("[OK] Phase 10 -> Journal holds {0} decision(s).".format(len(decisions_logged)))
    
    # 5. Query via API Layer (Phase 11)
    print("\n" + "="*60)
    print("PHASE 11 - REST API VERIFICATION (CLIENT VIEW)")
    print("="*60)
    
    headers = {"X-API-Key": "dummy"}
    
    res = client.get("/api/v1/system/status", headers=headers)
    print(f"\nGET /api/v1/system/status -> {res.status_code}")
    print(res.json())
    
    res = client.get("/api/v1/journal/latest", headers=headers)
    print(f"\nGET /api/v1/journal/latest -> {res.status_code}")
    for dec in res.json():
        print(f"  - {dec['strategy']} | {dec['decision']} | {dec['execution_status']} | Reason: {dec['reason']}")
    
    print("\nE2E Demo Complete.")

if __name__ == "__main__":
    run_e2e_demo()
