"""
Timestamp Tests — Verify created_at and updated_at behavior

Tests:
    - created_at is auto-populated on insert (all tables)
    - updated_at is auto-populated on create (mutable tables only)
    - updated_at changes when a mutable row is modified
    - Immutable tables have no updated_at column
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.enums import (
    AccountType,
    AssetClass,
    DecisionType,
    Direction,
    IndicatorType,
    LogLevel,
    MarketBias,
    OrderType,
    RiskCheckType,
    SettingValueType,
    SignalStatus,
    SignalType,
    Timeframe,
    TradeType,
    TrendHealth,
)
from app.database.models.account import Account
from app.database.models.candle import Candle
from app.database.models.decision_log import DecisionLog
from app.database.models.indicator_value import IndicatorValue
from app.database.models.instrument import Instrument
from app.database.models.market_analysis import MarketAnalysis
from app.database.models.market_holiday import MarketHoliday
from app.database.models.market_session import MarketSession
from app.database.models.order import Order
from app.database.models.position import Position
from app.database.models.risk_check import RiskCheck
from app.database.models.setting import Setting
from app.database.models.signal import Signal
from app.database.models.system_log import SystemLog
from app.database.models.trade import Trade


# ═══════════════════════════════════════════════════════════════════════════════
# created_at — auto-populated on insert (ALL tables)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreatedAt:
    """Every table must auto-populate created_at on insert."""

    def test_instrument_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_INST", name="Timestamp Test",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        assert inst.created_at is not None
        assert isinstance(inst.created_at, datetime)

    def test_account_created_at(self, db_session: Session):
        acct = Account(
            broker_name="TS_BKR", account_number="TS-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        assert acct.created_at is not None

    def test_candle_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_CANDLE", name="Candle TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        c = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100.5"),
        )
        db_session.add(c)
        db_session.flush()
        assert c.created_at is not None

    def test_market_session_created_at(self, db_session: Session):
        from datetime import time
        ms = MarketSession(
            exchange="TS_XCHG", day_of_week=1,
            open_time=time(9, 30), close_time=time(16, 0),
            timezone="UTC",
        )
        db_session.add(ms)
        db_session.flush()
        assert ms.created_at is not None

    def test_market_holiday_created_at(self, db_session: Session):
        from datetime import date
        mh = MarketHoliday(
            exchange="TS_XCHG",
            holiday_date=date(2026, 12, 25),
            name="Holiday TS",
        )
        db_session.add(mh)
        db_session.flush()
        assert mh.created_at is not None

    def test_indicator_value_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_IV", name="IV TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        c = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100"),
        )
        db_session.add(c)
        db_session.flush()
        iv = IndicatorValue(
            instrument_id=inst.id, candle_id=c.id,
            indicator_type=IndicatorType.RSI, timeframe=Timeframe.H1,
            value=Decimal("65"),
            calculated_at=datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc),
        )
        db_session.add(iv)
        db_session.flush()
        assert iv.created_at is not None

    def test_market_analysis_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_MA", name="MA TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        ma = MarketAnalysis(
            instrument_id=inst.id,
            timeframe=Timeframe.H1,
            analysis_timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            bias=MarketBias.NEUTRAL,
            trend_health=TrendHealth.HEALTHY,
            confidence_score=Decimal("50"),
        )
        db_session.add(ma)
        db_session.flush()
        assert ma.created_at is not None

    def test_signal_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_SIG", name="Sig TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        sig = Signal(
            instrument_id=inst.id,
            direction=Direction.LONG,
            signal_type=SignalType.ENTRY,
            timeframe=Timeframe.H1,
            confidence_score=Decimal("50"),
            strategy_version="v1.0",
        )
        db_session.add(sig)
        db_session.flush()
        assert sig.created_at is not None

    def test_risk_check_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_RC", name="RC TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        sig = Signal(
            instrument_id=inst.id,
            direction=Direction.LONG,
            signal_type=SignalType.ENTRY,
            timeframe=Timeframe.H1,
            confidence_score=Decimal("50"),
            strategy_version="v1.0",
        )
        db_session.add(sig)
        db_session.flush()
        rc = RiskCheck(
            signal_id=sig.id,
            check_type=RiskCheckType.POSITION_SIZE,
            passed=True,
        )
        db_session.add(rc)
        db_session.flush()
        assert rc.created_at is not None

    def test_order_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_ORD", name="Ord TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        acct = Account(
            broker_name="TS_ORD_BRK", account_number="TS-ORD-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        o = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="TS-ORD-ID",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(o)
        db_session.flush()
        assert o.created_at is not None

    def test_position_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_POS", name="Pos TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        acct = Account(
            broker_name="TS_POS_BRK", account_number="TS-POS-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        p = Position(
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG,
            entry_price=Decimal("100"), quantity=Decimal("1"),
            remaining_quantity=Decimal("1"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(p)
        db_session.flush()
        assert p.created_at is not None

    def test_trade_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_TRD", name="Trd TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        acct = Account(
            broker_name="TS_TRD_BRK", account_number="TS-TRD-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        o = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="TS-TRD-ORD",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(o)
        db_session.flush()
        p = Position(
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG,
            entry_price=Decimal("100"), quantity=Decimal("1"),
            remaining_quantity=Decimal("1"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(p)
        db_session.flush()
        t = Trade(
            position_id=p.id, order_id=o.id,
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG, trade_type=TradeType.ENTRY,
            quantity=Decimal("1"), price=Decimal("100"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(t)
        db_session.flush()
        assert t.created_at is not None

    def test_setting_created_at(self, db_session: Session):
        s = Setting(
            key="ts.test", value="x",
            value_type=SettingValueType.STRING, category="TEST",
        )
        db_session.add(s)
        db_session.flush()
        assert s.created_at is not None

    def test_system_log_created_at(self, db_session: Session):
        sl = SystemLog(
            level=LogLevel.INFO, module="app.test",
            message="TS log",
        )
        db_session.add(sl)
        db_session.flush()
        assert sl.created_at is not None

    def test_decision_log_created_at(self, db_session: Session):
        inst = Instrument(
            symbol="TS_DL", name="DL TS",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        dl = DecisionLog(
            instrument_id=inst.id,
            decision_type=DecisionType.ENTRY,
            decision_context={},
            reason="TS test",
            confidence_score=Decimal("50"),
            engine_version="v1.0",
        )
        db_session.add(dl)
        db_session.flush()
        assert dl.created_at is not None


# ═══════════════════════════════════════════════════════════════════════════════
# updated_at — auto-populated on create (mutable tables only)
# ═══════════════════════════════════════════════════════════════════════════════


class TestUpdatedAtOnCreate:
    """Mutable tables must auto-populate updated_at on insert."""

    def test_instrument_updated_at_on_create(self, db_session: Session):
        inst = Instrument(
            symbol="UA_INST", name="UA Test",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        assert inst.updated_at is not None

    def test_account_updated_at_on_create(self, db_session: Session):
        acct = Account(
            broker_name="UA_BKR", account_number="UA-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        assert acct.updated_at is not None

    def test_signal_updated_at_on_create(self, db_session: Session):
        inst = Instrument(
            symbol="UA_SIG", name="UA Sig",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        sig = Signal(
            instrument_id=inst.id,
            direction=Direction.LONG,
            signal_type=SignalType.ENTRY,
            timeframe=Timeframe.H1,
            confidence_score=Decimal("50"),
            strategy_version="v1.0",
        )
        db_session.add(sig)
        db_session.flush()
        assert sig.updated_at is not None

    def test_order_updated_at_on_create(self, db_session: Session):
        inst = Instrument(
            symbol="UA_ORD", name="UA Ord",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        acct = Account(
            broker_name="UA_ORD_BRK", account_number="UA-ORD-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        o = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="UA-ORD-ID",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(o)
        db_session.flush()
        assert o.updated_at is not None

    def test_position_updated_at_on_create(self, db_session: Session):
        inst = Instrument(
            symbol="UA_POS", name="UA Pos",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        acct = Account(
            broker_name="UA_POS_BRK", account_number="UA-POS-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        p = Position(
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG,
            entry_price=Decimal("100"), quantity=Decimal("1"),
            remaining_quantity=Decimal("1"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(p)
        db_session.flush()
        assert p.updated_at is not None

    def test_setting_updated_at_on_create(self, db_session: Session):
        s = Setting(
            key="ua.test", value="y",
            value_type=SettingValueType.STRING, category="TEST",
        )
        db_session.add(s)
        db_session.flush()
        assert s.updated_at is not None


# ═══════════════════════════════════════════════════════════════════════════════
# updated_at — changes on modification
# ═══════════════════════════════════════════════════════════════════════════════


class TestUpdatedAtOnUpdate:
    """updated_at must change when a mutable row is modified."""

    def test_instrument_updated_at_changes(self, db_session: Session):
        inst = Instrument(
            symbol="UU_INST", name="UU Test",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        original = inst.updated_at
        inst.tick_size = Decimal("0.05")
        db_session.flush()
        assert inst.updated_at is not None
        assert inst.updated_at >= original

    def test_account_updated_at_changes(self, db_session: Session):
        acct = Account(
            broker_name="UU_BKR", account_number="UU-001",
            account_type=AccountType.DEMO, currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        original = acct.updated_at
        acct.balance = Decimal("50000.00")
        db_session.flush()
        assert acct.updated_at is not None
        assert acct.updated_at >= original

    def test_signal_updated_at_changes(self, db_session: Session):
        inst = Instrument(
            symbol="UU_SIG", name="UU Sig",
            asset_class=AssetClass.INDEX, exchange="TEST",
            tick_size=Decimal("0.01"), currency="USD",
        )
        db_session.add(inst)
        db_session.flush()
        sig = Signal(
            instrument_id=inst.id,
            direction=Direction.LONG,
            signal_type=SignalType.ENTRY,
            timeframe=Timeframe.H1,
            confidence_score=Decimal("50"),
            strategy_version="v1.0",
        )
        db_session.add(sig)
        db_session.flush()
        original = sig.updated_at
        sig.status = SignalStatus.APPROVED
        db_session.flush()
        assert sig.updated_at is not None
        assert sig.updated_at >= original


# ═══════════════════════════════════════════════════════════════════════════════
# Immutable tables — no updated_at column
# ═══════════════════════════════════════════════════════════════════════════════


class TestImmutableNoUpdatedAt:
    """Immutable tables must NOT have an updated_at column."""

    IMMUTABLE_MODELS = [
        Candle,
        Trade,
        DecisionLog,
        IndicatorValue,
        MarketAnalysis,
        RiskCheck,
        MarketSession,
        MarketHoliday,
        SystemLog,
    ]

    def test_immutable_models_have_no_updated_at(self):
        """Every immutable model should NOT define updated_at."""
        for model in self.IMMUTABLE_MODELS:
            assert not hasattr(model, "updated_at"), (
                f"{model.__name__} is immutable but has updated_at"
            )