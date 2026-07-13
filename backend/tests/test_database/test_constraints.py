"""
Database Constraint Tests — UNIQUE, FK, and nullable constraints

Verifies that:
    - UNIQUE constraints reject duplicates
    - Foreign keys enforce referential integrity (RESTRICT)
    - Nullable FK columns accept NULL
    - Required columns reject NULL
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.enums import (
    AccountType,
    AssetClass,
    Direction,
    IndicatorType,
    OrderType,
    PositionStatus,
    SignalType,
    Timeframe,
    TradeType,
)
from app.database.models.account import Account
from app.database.models.candle import Candle
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
from app.database.models.trade import Trade

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _instrument(db: Session, symbol: str = "CSTR_TEST") -> Instrument:
    inst = Instrument(
        symbol=symbol, name="Constraint Test",
        asset_class=AssetClass.INDEX, exchange="TEST",
        tick_size=Decimal("0.01"), currency="USD",
    )
    db.add(inst)
    db.flush()
    return inst


def _account(db: Session, broker: str = "CSTR_BRK", number: str = "CSTR-001") -> Account:
    acct = Account(
        broker_name=broker, account_number=number,
        account_type=AccountType.DEMO, currency="USD",
    )
    db.add(acct)
    db.flush()
    return acct


def _signal(db: Session, instrument_id: int) -> Signal:
    sig = Signal(
        instrument_id=instrument_id, direction=Direction.LONG,
        signal_type=SignalType.ENTRY, timeframe=Timeframe.H1,
        confidence_score=Decimal("50"), strategy_version="v1.0",
    )
    db.add(sig)
    db.flush()
    return sig


# ═══════════════════════════════════════════════════════════════════════════════
# UNIQUE Constraints
# ═══════════════════════════════════════════════════════════════════════════════


class TestUniqueConstraints:
    """Verify that UNIQUE constraints prevent duplicate rows."""

    def test_instrument_symbol_unique(self, db_session: Session):
        inst1 = _instrument(db_session, symbol="UNIQUE_SYM")
        inst2 = Instrument(
            symbol="UNIQUE_SYM", name="Duplicate",
            asset_class=AssetClass.FOREX, exchange="T2",
            tick_size=Decimal("0.0001"), currency="USD",
        )
        db_session.add(inst2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_candle_instrument_timestamp_unique(self, db_session: Session):
        inst = _instrument(db_session)
        ts = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
        c1 = Candle(
            instrument_id=inst.id, timestamp=ts,
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100.5"),
        )
        db_session.add(c1)
        db_session.flush()
        c2 = Candle(
            instrument_id=inst.id, timestamp=ts,
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100.5"),
        )
        db_session.add(c2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_market_session_exchange_day_unique(self, db_session: Session):
        from datetime import time
        ms1 = MarketSession(exchange="CME", day_of_week=1,
                            open_time=time(9, 30), close_time=time(16, 0),
                            timezone="America/New_York")
        db_session.add(ms1)
        db_session.flush()
        ms2 = MarketSession(exchange="CME", day_of_week=1,
                            open_time=time(8, 0), close_time=time(14, 0),
                            timezone="America/Chicago")
        db_session.add(ms2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_order_client_order_id_unique(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        o1 = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="DUP-ORDER-ID",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(o1)
        db_session.flush()
        o2 = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="DUP-ORDER-ID",
            direction=Direction.SHORT, order_type=OrderType.LIMIT,
            quantity=Decimal("2"), price=Decimal("100"),
        )
        db_session.add(o2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_settings_key_unique(self, db_session: Session):
        from app.database.enums import SettingValueType
        s1 = Setting(key="unique.key", value="first",
                     value_type=SettingValueType.STRING, category="TEST")
        db_session.add(s1)
        db_session.flush()
        s2 = Setting(key="unique.key", value="second",
                     value_type=SettingValueType.STRING, category="TEST")
        db_session.add(s2)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_indicator_values_unique_composite(self, db_session: Session):
        inst = _instrument(db_session)
        ts = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
        candle = Candle(instrument_id=inst.id, timestamp=ts,
                       open=Decimal("100"), high=Decimal("101"),
                       low=Decimal("99"), close=Decimal("100.5"))
        db_session.add(candle)
        db_session.flush()
        calc_at = datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc)
        iv1 = IndicatorValue(
            instrument_id=inst.id, candle_id=candle.id,
            indicator_type=IndicatorType.RSI, timeframe=Timeframe.H1,
            value=Decimal("65"), calculated_at=calc_at,
        )
        db_session.add(iv1)
        db_session.flush()
        iv2 = IndicatorValue(
            instrument_id=inst.id, candle_id=candle.id,
            indicator_type=IndicatorType.RSI, timeframe=Timeframe.H1,
            value=Decimal("70"), calculated_at=calc_at,
        )
        db_session.add(iv2)
        with pytest.raises(IntegrityError):
            db_session.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# Foreign Key Constraints — RESTRICT
# ═══════════════════════════════════════════════════════════════════════════════


class TestForeignKeyRestrict:
    """Verify that deleting a parent row with children fails (RESTRICT)."""

    def test_cannot_delete_instrument_with_candles(self, db_session: Session):
        inst = _instrument(db_session)
        candle = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100.5"),
        )
        db_session.add(candle)
        db_session.flush()
        with pytest.raises(IntegrityError):
            db_session.delete(inst)
            db_session.flush()

    def test_cannot_delete_signal_with_risk_checks(self, db_session: Session):
        inst = _instrument(db_session)
        sig = _signal(db_session, inst.id)
        from app.database.enums import RiskCheckType
        rc = RiskCheck(signal_id=sig.id, check_type=RiskCheckType.POSITION_SIZE,
                       passed=True)
        db_session.add(rc)
        db_session.flush()
        with pytest.raises(IntegrityError):
            db_session.delete(sig)
            db_session.flush()

    def test_cannot_delete_account_with_orders(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        order = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="FK-TEST-001",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(order)
        db_session.flush()
        with pytest.raises(IntegrityError):
            db_session.delete(acct)
            db_session.flush()

    def test_cannot_delete_position_with_trades(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        order = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="FK-TRADE-001",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(order)
        db_session.flush()
        pos = Position(
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG,
            entry_price=Decimal("100"), quantity=Decimal("1"),
            remaining_quantity=Decimal("1"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(pos)
        db_session.flush()
        trade = Trade(
            position_id=pos.id, order_id=order.id,
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG, trade_type=TradeType.ENTRY,
            quantity=Decimal("1"), price=Decimal("100"),
            executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
        )
        db_session.add(trade)
        db_session.flush()
        with pytest.raises(IntegrityError):
            db_session.delete(pos)
            db_session.flush()

    def test_invalid_fk_rejected(self, db_session: Session):
        """Inserting a row with a non-existent FK raises IntegrityError."""
        candle = Candle(
            instrument_id=99999,  # does not exist
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100.5"),
        )
        db_session.add(candle)
        with pytest.raises(IntegrityError):
            db_session.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# Nullable Columns
# ═══════════════════════════════════════════════════════════════════════════════


class TestNullableColumns:
    """Verify nullable columns accept NULL and required columns reject NULL."""

    def test_order_signal_id_nullable(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        o = Order(
            signal_id=None,
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="NULLABLE-SIG-001",
            direction=Direction.LONG, order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )
        db_session.add(o)
        db_session.flush()
        assert o.signal_id is None

    def test_decision_log_signal_id_nullable(self, db_session: Session):
        from app.database.enums import DecisionType
        from app.database.models.decision_log import DecisionLog
        inst = _instrument(db_session)
        dl = DecisionLog(
            signal_id=None,
            instrument_id=inst.id,
            decision_type=DecisionType.ENTRY,
            decision_context={},
            reason="Test",
            confidence_score=Decimal("50"),
            engine_version="v1.0",
        )
        db_session.add(dl)
        db_session.flush()
        assert dl.signal_id is None

    def test_instrument_symbol_not_null(self, db_session: Session):
        inst = Instrument(
            symbol=None,
            name="No Symbol",
            asset_class=AssetClass.INDEX,
            exchange="T",
            tick_size=Decimal("0.01"),
            currency="USD",
        )
        db_session.add(inst)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_candle_open_not_null(self, db_session: Session):
        inst = _instrument(db_session)
        c = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=None,
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100"),
        )
        db_session.add(c)
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_position_entry_price_not_null(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        p = Position(
            instrument_id=inst.id, account_id=acct.id,
            direction=Direction.LONG,
            entry_price=None,
            quantity=Decimal("1"),
            remaining_quantity=Decimal("1"),
            opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(p)
        with pytest.raises(IntegrityError):
            db_session.flush()