"""
Database Model Tests — CRUD, relationships, and __repr__

Tests every model:
    - Can be created and flushed (no schema errors)
    - Can be queried back by ID
    - __repr__ returns expected format
    - Relationships load correctly (eager selectin)
"""
from datetime import date, datetime, time, timezone
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.database.enums import (
    AccountType,
    AssetClass,
    DecisionOutcome,
    DecisionType,
    Direction,
    IndicatorType,
    LogLevel,
    MarketBias,
    OrderStatus,
    OrderType,
    PositionStatus,
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
# Helper: reusable instrument fixture (needed by most FK-dependent models)
# ═══════════════════════════════════════════════════════════════════════════════


def _create_instrument(db: Session, symbol: str = "TEST_US") -> Instrument:
    inst = Instrument(
        symbol=symbol,
        name=f"{symbol} Test Instrument",
        asset_class=AssetClass.INDEX,
        exchange="TEST",
        tick_size=Decimal("0.01"),
        contract_size=Decimal("1.0"),
        currency="USD",
    )
    db.add(inst)
    db.flush()
    return inst


def _create_account(db: Session) -> Account:
    acct = Account(
        broker_name="TestBroker",
        account_number="TEST-001",
        account_type=AccountType.DEMO,
        currency="USD",
        balance=Decimal("100000.00"),
        is_default=True,
    )
    db.add(acct)
    db.flush()
    return acct


def _create_candle(db: Session, instrument_id: int) -> Candle:
    c = Candle(
        instrument_id=instrument_id,
        timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        open=Decimal("100.0"),
        high=Decimal("101.0"),
        low=Decimal("99.0"),
        close=Decimal("100.5"),
        volume=Decimal("1000"),
    )
    db.add(c)
    db.flush()
    return c


def _create_signal(db: Session, instrument_id: int) -> Signal:
    sig = Signal(
        instrument_id=instrument_id,
        direction=Direction.LONG,
        signal_type=SignalType.ENTRY,
        timeframe=Timeframe.H1,
        entry_price=Decimal("100.50"),
        stop_loss=Decimal("99.50"),
        take_profit=Decimal("102.00"),
        confidence_score=Decimal("75.00"),
        strategy_version="v1.0",
        status=SignalStatus.PENDING,
    )
    db.add(sig)
    db.flush()
    return sig


def _create_order(db: Session, instrument_id: int, account_id: int, signal_id: int | None = None) -> Order:
    o = Order(
        signal_id=signal_id,
        instrument_id=instrument_id,
        account_id=account_id,
        client_order_id="AGS-20260710-000001",
        direction=Direction.LONG,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0"),
        status=OrderStatus.PENDING,
    )
    db.add(o)
    db.flush()
    return o


def _create_position(db: Session, instrument_id: int, account_id: int) -> Position:
    p = Position(
        instrument_id=instrument_id,
        account_id=account_id,
        direction=Direction.LONG,
        status=PositionStatus.OPEN,
        entry_price=Decimal("100.00"),
        quantity=Decimal("1.0"),
        remaining_quantity=Decimal("1.0"),
        opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
    )
    db.add(p)
    db.flush()
    return p


# ═══════════════════════════════════════════════════════════════════════════════
# Instrument
# ═══════════════════════════════════════════════════════════════════════════════


class TestInstrument:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        assert inst.id is not None

    def test_query_by_id(self, db_session: Session):
        inst = _create_instrument(db_session)
        found = db_session.get(Instrument, inst.id)
        assert found is not None
        assert found.symbol == "TEST_US"

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session, symbol="EURUSD")
        r = repr(inst)
        assert "Instrument" in r
        assert "EURUSD" in r

    def test_asset_class_values(self, db_session: Session):
        for ac in AssetClass:
            inst = Instrument(
                symbol=f"T{ac.value}",
                name=f"Test {ac.value}",
                asset_class=ac,
                exchange="T",
                tick_size=Decimal("0.01"),
                currency="USD",
            )
            db_session.add(inst)
            db_session.flush()
            assert inst.asset_class == ac


# ═══════════════════════════════════════════════════════════════════════════════
# Candle
# ═══════════════════════════════════════════════════════════════════════════════


class TestCandle:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        c = _create_candle(db_session, inst.id)
        assert c.id is not None

    def test_relationship_to_instrument(self, db_session: Session):
        inst = _create_instrument(db_session)
        c = _create_candle(db_session, inst.id)
        assert c.instrument.id == inst.id

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        c = _create_candle(db_session, inst.id)
        r = repr(c)
        assert "Candle" in r

    def test_numeric_precision(self, db_session: Session):
        inst = _create_instrument(db_session)
        c = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("1.08542"),
            high=Decimal("1.08600"),
            low=Decimal("1.08500"),
            close=Decimal("1.08580"),
            volume=Decimal("0.00001234"),
        )
        db_session.add(c)
        db_session.flush()
        retrieved = db_session.get(Candle, c.id)
        assert retrieved is not None
        assert retrieved.open == Decimal("1.08542")
        assert retrieved.volume == Decimal("0.00001234")

    def test_volume_default(self, db_session: Session):
        inst = _create_instrument(db_session)
        c = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 13, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100.0"),
            high=Decimal("100.0"),
            low=Decimal("100.0"),
            close=Decimal("100.0"),
        )
        db_session.add(c)
        db_session.flush()
        retrieved = db_session.get(Candle, c.id)
        assert retrieved is not None
        assert retrieved.volume == Decimal("0")


# ═══════════════════════════════════════════════════════════════════════════════
# MarketSession
# ═══════════════════════════════════════════════════════════════════════════════


class TestMarketSession:
    def test_create(self, db_session: Session):
        ms = MarketSession(
            exchange="CME",
            day_of_week=1,
            open_time=time(9, 30),
            close_time=time(16, 0),
            timezone="America/New_York",
        )
        db_session.add(ms)
        db_session.flush()
        assert ms.id is not None

    def test_repr(self, db_session: Session):
        ms = MarketSession(
            exchange="CME", day_of_week=1,
            open_time=time(9, 30), close_time=time(16, 0),
            timezone="America/New_York",
        )
        db_session.add(ms)
        db_session.flush()
        assert "CME" in repr(ms)


# ═══════════════════════════════════════════════════════════════════════════════
# MarketHoliday
# ═══════════════════════════════════════════════════════════════════════════════


class TestMarketHoliday:
    def test_create_full_day(self, db_session: Session):
        mh = MarketHoliday(
            exchange="CME",
            holiday_date=date(2026, 12, 25),
            name="Christmas",
            is_full_day=True,
        )
        db_session.add(mh)
        db_session.flush()
        assert mh.id is not None
        assert mh.early_close_time is None

    def test_create_half_day(self, db_session: Session):
        mh = MarketHoliday(
            exchange="CME",
            holiday_date=date(2026, 12, 24),
            name="Christmas Eve",
            is_full_day=False,
            early_close_time=time(13, 0),
        )
        db_session.add(mh)
        db_session.flush()
        assert mh.early_close_time == time(13, 0)

    def test_repr(self, db_session: Session):
        mh = MarketHoliday(
            exchange="CME", holiday_date=date(2026, 12, 25),
            name="Christmas",
        )
        db_session.add(mh)
        db_session.flush()
        assert "Christmas" not in repr(mh)  # repr uses exchange + date, not name
        assert "CME" in repr(mh)


# ═══════════════════════════════════════════════════════════════════════════════
# IndicatorValue
# ═══════════════════════════════════════════════════════════════════════════════


class TestIndicatorValue:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        candle = _create_candle(db_session, inst.id)
        iv = IndicatorValue(
            instrument_id=inst.id,
            candle_id=candle.id,
            indicator_type=IndicatorType.RSI,
            timeframe=Timeframe.H1,
            value=Decimal("65.5"),
            calculated_at=datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc),
        )
        db_session.add(iv)
        db_session.flush()
        assert iv.id is not None

    def test_metadata_jsonb(self, db_session: Session):
        inst = _create_instrument(db_session)
        candle = _create_candle(db_session, inst.id)
        iv = IndicatorValue(
            instrument_id=inst.id,
            candle_id=candle.id,
            indicator_type=IndicatorType.MACD,
            timeframe=Timeframe.H1,
            value=Decimal("0.52"),
            calculated_at=datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc),
            metadata_json={"signal": 0.5, "histogram": 0.2},
        )
        db_session.add(iv)
        db_session.flush()
        retrieved = db_session.get(IndicatorValue, iv.id)
        assert retrieved is not None
        assert retrieved.metadata_json == {"signal": 0.5, "histogram": 0.2}

    def test_relationship_to_candle(self, db_session: Session):
        inst = _create_instrument(db_session)
        candle = _create_candle(db_session, inst.id)
        iv = IndicatorValue(
            instrument_id=inst.id,
            candle_id=candle.id,
            indicator_type=IndicatorType.EMA,
            timeframe=Timeframe.M5,
            value=Decimal("100.2"),
            calculated_at=datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc),
        )
        db_session.add(iv)
        db_session.flush()
        assert iv.candle.id == candle.id

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        candle = _create_candle(db_session, inst.id)
        iv = IndicatorValue(
            instrument_id=inst.id,
            candle_id=candle.id,
            indicator_type=IndicatorType.ATR,
            timeframe=Timeframe.H1,
            value=Decimal("0.05"),
            calculated_at=datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc),
        )
        db_session.add(iv)
        db_session.flush()
        r = repr(iv)
        assert "ATR" in r
        assert "H1" in r


# ═══════════════════════════════════════════════════════════════════════════════
# MarketAnalysis
# ═══════════════════════════════════════════════════════════════════════════════


class TestMarketAnalysis:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        ma = MarketAnalysis(
            instrument_id=inst.id,
            timeframe=Timeframe.H1,
            analysis_timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            bias=MarketBias.BULLISH,
            trend_health=TrendHealth.HEALTHY,
            confidence_score=Decimal("80.00"),
        )
        db_session.add(ma)
        db_session.flush()
        assert ma.id is not None

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        ma = MarketAnalysis(
            instrument_id=inst.id,
            timeframe=Timeframe.H4,
            analysis_timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            bias=MarketBias.BEARISH,
            trend_health=TrendHealth.WEAK,
            confidence_score=Decimal("30.00"),
        )
        db_session.add(ma)
        db_session.flush()
        assert "BEARISH" in repr(ma)


# ═══════════════════════════════════════════════════════════════════════════════
# Signal
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignal:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        assert sig.id is not None

    def test_default_status(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = Signal(
            instrument_id=inst.id,
            direction=Direction.SHORT,
            signal_type=SignalType.EXIT,
            timeframe=Timeframe.M15,
            confidence_score=Decimal("50.00"),
            strategy_version="v1.0",
        )
        db_session.add(sig)
        db_session.flush()
        assert sig.status == SignalStatus.PENDING

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        assert "LONG" in repr(sig)
        assert "ENTRY" in repr(sig)

    def test_nullable_entry_price(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = Signal(
            instrument_id=inst.id,
            direction=Direction.LONG,
            signal_type=SignalType.ENTRY,
            timeframe=Timeframe.H1,
            confidence_score=Decimal("60.00"),
            strategy_version="v1.0",
            entry_price=None,
        )
        db_session.add(sig)
        db_session.flush()
        assert sig.entry_price is None


# ═══════════════════════════════════════════════════════════════════════════════
# RiskCheck
# ═══════════════════════════════════════════════════════════════════════════════


class TestRiskCheck:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        rc = RiskCheck(
            signal_id=sig.id,
            check_type=RiskCheckType.POSITION_SIZE,
            passed=True,
            check_value=Decimal("1.0"),
            threshold_value=Decimal("5.0"),
        )
        db_session.add(rc)
        db_session.flush()
        assert rc.id is not None

    def test_failed_check(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        rc = RiskCheck(
            signal_id=sig.id,
            check_type=RiskCheckType.MAX_DRAWDOWN,
            passed=False,
            message="Drawdown exceeds 5% limit",
        )
        db_session.add(rc)
        db_session.flush()
        assert rc.passed is False
        assert rc.message == "Drawdown exceeds 5% limit"

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        rc = RiskCheck(
            signal_id=sig.id,
            check_type=RiskCheckType.EXPOSURE_LIMIT,
            passed=True,
        )
        db_session.add(rc)
        db_session.flush()
        r = repr(rc)
        assert "EXPOSURE_LIMIT" in r
        assert "True" in r


# ═══════════════════════════════════════════════════════════════════════════════
# Account
# ═══════════════════════════════════════════════════════════════════════════════


class TestAccount:
    def test_create(self, db_session: Session):
        acct = _create_account(db_session)
        assert acct.id is not None

    def test_account_types(self, db_session: Session):
        for at in AccountType:
            acct = Account(
                broker_name=f"Broker_{at.value}",
                account_number=f"ACC-{at.value}",
                account_type=at,
                currency="USD",
            )
            db_session.add(acct)
            db_session.flush()
            assert acct.account_type == at

    def test_repr(self, db_session: Session):
        acct = _create_account(db_session)
        r = repr(acct)
        assert "TestBroker" in r
        assert "DEMO" in r

    def test_balance_default(self, db_session: Session):
        acct = Account(
            broker_name="MinBroker",
            account_number="MIN-001",
            account_type=AccountType.DEMO,
            currency="USD",
        )
        db_session.add(acct)
        db_session.flush()
        assert acct.balance == Decimal("0")


# ═══════════════════════════════════════════════════════════════════════════════
# Order
# ═══════════════════════════════════════════════════════════════════════════════


class TestOrder:
    def test_create_with_signal(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        sig = _create_signal(db_session, inst.id)
        o = _create_order(db_session, inst.id, acct.id, signal_id=sig.id)
        assert o.id is not None
        assert o.signal_id == sig.id

    def test_create_without_signal(self, db_session: Session):
        """Manual orders have nullable signal_id."""
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        o = _create_order(db_session, inst.id, acct.id, signal_id=None)
        assert o.signal_id is None

    def test_order_types(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        for ot in OrderType:
            o = Order(
                instrument_id=inst.id,
                account_id=acct.id,
                client_order_id=f"AGS-{ot.value}-001",
                direction=Direction.LONG,
                order_type=ot,
                quantity=Decimal("1.0"),
            )
            db_session.add(o)
            db_session.flush()
            assert o.order_type == ot

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        o = _create_order(db_session, inst.id, acct.id)
        r = repr(o)
        assert "AGS-20260710-000001" in r


# ═══════════════════════════════════════════════════════════════════════════════
# Position
# ═══════════════════════════════════════════════════════════════════════════════


class TestPosition:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        p = _create_position(db_session, inst.id, acct.id)
        assert p.id is not None

    def test_default_status(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        p = Position(
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.SHORT,
            entry_price=Decimal("100.00"),
            quantity=Decimal("2.0"),
            remaining_quantity=Decimal("2.0"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(p)
        db_session.flush()
        assert p.status == PositionStatus.OPEN

    def test_pnl_nullable(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        p = Position(
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.LONG,
            entry_price=Decimal("100.00"),
            quantity=Decimal("1.0"),
            remaining_quantity=Decimal("1.0"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(p)
        db_session.flush()
        assert p.unrealized_pnl is None
        assert p.realized_pnl is None

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        p = _create_position(db_session, inst.id, acct.id)
        assert "LONG" in repr(p)
        assert "OPEN" in repr(p)


# ═══════════════════════════════════════════════════════════════════════════════
# Trade
# ═══════════════════════════════════════════════════════════════════════════════


class TestTrade:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        order = _create_order(db_session, inst.id, acct.id)
        position = _create_position(db_session, inst.id, acct.id)
        t = Trade(
            position_id=position.id,
            order_id=order.id,
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.LONG,
            trade_type=TradeType.ENTRY,
            quantity=Decimal("1.0"),
            price=Decimal("100.50"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(t)
        db_session.flush()
        assert t.id is not None

    def test_entry_pnl_null(self, db_session: Session):
        """Entry trades should have NULL pnl (not 0)."""
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        order = _create_order(db_session, inst.id, acct.id)
        position = _create_position(db_session, inst.id, acct.id)
        t = Trade(
            position_id=position.id,
            order_id=order.id,
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.LONG,
            trade_type=TradeType.ENTRY,
            quantity=Decimal("1.0"),
            price=Decimal("100.00"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(t)
        db_session.flush()
        assert t.pnl is None

    def test_exit_trade_with_pnl(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        order = _create_order(db_session, inst.id, acct.id)
        position = _create_position(db_session, inst.id, acct.id)
        t = Trade(
            position_id=position.id,
            order_id=order.id,
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.SHORT,
            trade_type=TradeType.EXIT,
            quantity=Decimal("1.0"),
            price=Decimal("101.00"),
            pnl=Decimal("-1.00"),
            executed_at=datetime(2026, 7, 10, 14, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(t)
        db_session.flush()
        assert t.pnl == Decimal("-1.00")

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        order = _create_order(db_session, inst.id, acct.id)
        position = _create_position(db_session, inst.id, acct.id)
        t = Trade(
            position_id=position.id,
            order_id=order.id,
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.LONG,
            trade_type=TradeType.ENTRY,
            quantity=Decimal("1.0"),
            price=Decimal("100.50"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(t)
        db_session.flush()
        assert "ENTRY" in repr(t)
        assert "100.50" in repr(t)

    def test_commission_default(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        order = _create_order(db_session, inst.id, acct.id)
        position = _create_position(db_session, inst.id, acct.id)
        t = Trade(
            position_id=position.id,
            order_id=order.id,
            instrument_id=inst.id,
            account_id=acct.id,
            direction=Direction.LONG,
            trade_type=TradeType.ENTRY,
            quantity=Decimal("1.0"),
            price=Decimal("100.00"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(t)
        db_session.flush()
        retrieved = db_session.get(Trade, t.id)
        assert retrieved is not None
        assert retrieved.commission == Decimal("0")


# ═══════════════════════════════════════════════════════════════════════════════
# Setting
# ═══════════════════════════════════════════════════════════════════════════════


class TestSetting:
    def test_create(self, db_session: Session):
        s = Setting(
            key="risk.max_position_size",
            value="5.0",
            value_type=SettingValueType.FLOAT,
            category="RISK",
            description="Maximum position size in lots",
        )
        db_session.add(s)
        db_session.flush()
        assert s.id is not None

    def test_repr(self, db_session: Session):
        s = Setting(
            key="test.key", value="hello",
            value_type=SettingValueType.STRING, category="SYSTEM",
        )
        db_session.add(s)
        db_session.flush()
        assert "test.key" in repr(s)


# ═══════════════════════════════════════════════════════════════════════════════
# SystemLog
# ═══════════════════════════════════════════════════════════════════════════════


class TestSystemLog:
    def test_create(self, db_session: Session):
        sl = SystemLog(
            level=LogLevel.INFO,
            module="app.test",
            message="Test log message",
        )
        db_session.add(sl)
        db_session.flush()
        assert sl.id is not None

    def test_with_metadata(self, db_session: Session):
        sl = SystemLog(
            level=LogLevel.ERROR,
            module="app.market",
            message="Connection failed",
            metadata_json={"error_code": 503, "retry_count": 3},
        )
        db_session.add(sl)
        db_session.flush()
        retrieved = db_session.get(SystemLog, sl.id)
        assert retrieved is not None
        assert retrieved.metadata_json == {"error_code": 503, "retry_count": 3}

    def test_repr(self, db_session: Session):
        sl = SystemLog(
            level=LogLevel.WARNING,
            module="app.risk",
            message="Warning",
        )
        db_session.add(sl)
        db_session.flush()
        r = repr(sl)
        assert "WARNING" in r
        assert "app.risk" in r


# ═══════════════════════════════════════════════════════════════════════════════
# DecisionLog
# ═══════════════════════════════════════════════════════════════════════════════


class TestDecisionLog:
    def test_create(self, db_session: Session):
        inst = _create_instrument(db_session)
        dl = DecisionLog(
            instrument_id=inst.id,
            decision_type=DecisionType.ENTRY,
            decision_context={"indicators": {"RSI": 35}},
            reason="RSI oversold, bullish divergence",
            confidence_score=Decimal("72.00"),
            engine_version="v1.0",
            outcome=DecisionOutcome.PENDING,
        )
        db_session.add(dl)
        db_session.flush()
        assert dl.id is not None

    def test_with_signal(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        dl = DecisionLog(
            signal_id=sig.id,
            instrument_id=inst.id,
            decision_type=DecisionType.ENTRY,
            decision_context={"indicators": {"RSI": 28}},
            reason="RSI oversold",
            confidence_score=Decimal("80.00"),
            engine_version="v1.0",
            outcome=DecisionOutcome.SUCCESS,
        )
        db_session.add(dl)
        db_session.flush()
        assert dl.signal_id == sig.id

    def test_repr(self, db_session: Session):
        inst = _create_instrument(db_session)
        dl = DecisionLog(
            instrument_id=inst.id,
            decision_type=DecisionType.REJECT,
            decision_context={},
            reason="Risk limit",
            confidence_score=Decimal("50.00"),
            engine_version="v1.0",
        )
        db_session.add(dl)
        db_session.flush()
        r = repr(dl)
        assert "REJECT" in r
        assert "PENDING" in r

    def test_without_signal(self, db_session: Session):
        inst = _create_instrument(db_session)
        dl = DecisionLog(
            instrument_id=inst.id,
            decision_type=DecisionType.CANCEL,
            decision_context={},
            reason="No valid setup",
            confidence_score=Decimal("10.00"),
            engine_version="v1.0",
            signal_id=None,
        )
        db_session.add(dl)
        db_session.flush()
        assert dl.signal_id is None


# ═══════════════════════════════════════════════════════════════════════════════
# Relationship Loading (eager selectin)
# ═══════════════════════════════════════════════════════════════════════════════


class TestRelationshipLoading:
    def test_instrument_has_candles(self, db_session: Session):
        inst = _create_instrument(db_session)
        c1 = _create_candle(db_session, inst.id)
        c2 = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
            open=Decimal("101"), high=Decimal("102"),
            low=Decimal("100"), close=Decimal("101.5"),
            volume=Decimal("500"),
        )
        db_session.add(c2)
        db_session.flush()
        # refresh to load relationships
        db_session.refresh(inst)
        assert len(inst.candles) == 2

    def test_signal_has_risk_checks(self, db_session: Session):
        inst = _create_instrument(db_session)
        sig = _create_signal(db_session, inst.id)
        rc1 = RiskCheck(signal_id=sig.id, check_type=RiskCheckType.POSITION_SIZE, passed=True)
        rc2 = RiskCheck(signal_id=sig.id, check_type=RiskCheckType.STOP_LOSS_DISTANCE, passed=True)
        db_session.add_all([rc1, rc2])
        db_session.flush()
        db_session.refresh(sig)
        assert len(sig.risk_checks) == 2

    def test_position_has_trades(self, db_session: Session):
        inst = _create_instrument(db_session)
        acct = _create_account(db_session)
        order = _create_order(db_session, inst.id, acct.id)
        position = _create_position(db_session, inst.id, acct.id)
        t1 = Trade(
            position_id=position.id, order_id=order.id,
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG, trade_type=TradeType.ENTRY,
            quantity=Decimal("1.0"), price=Decimal("100.0"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(t1)
        db_session.flush()
        db_session.refresh(position)
        assert len(position.trades) == 1