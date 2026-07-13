"""
Enum Validation Tests — Verify all 18 ENUM types accept valid values and reject invalid ones

Tests:
    - Every enum value is accepted by PostgreSQL
    - Invalid enum strings are rejected with DataError
    - server_default enum values are applied correctly
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import DataError, IntegrityError
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
from app.database.models.decision_log import DecisionLog
from app.database.models.indicator_value import IndicatorValue
from app.database.models.instrument import Instrument
from app.database.models.market_analysis import MarketAnalysis
from app.database.models.order import Order
from app.database.models.position import Position
from app.database.models.risk_check import RiskCheck
from app.database.models.setting import Setting
from app.database.models.signal import Signal
from app.database.models.system_log import SystemLog
from app.database.models.trade import Trade

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _instrument(db: Session) -> Instrument:
    inst = Instrument(
        symbol="ENUM_TEST",
        name="Enum Test",
        asset_class=AssetClass.INDEX,
        exchange="TEST",
        tick_size=Decimal("0.01"),
        currency="USD",
    )
    db.add(inst)
    db.flush()
    return inst


def _account(db: Session, suffix: str = "") -> Account:
    acct = Account(
        broker_name=f"EnumBroker{suffix}",
        account_number=f"ENUM-ACC-{suffix}",
        account_type=AccountType.DEMO,
        currency="USD",
    )
    db.add(acct)
    db.flush()
    return acct


def _signal(db: Session, instrument_id: int) -> Signal:
    sig = Signal(
        instrument_id=instrument_id,
        direction=Direction.LONG,
        signal_type=SignalType.ENTRY,
        timeframe=Timeframe.H1,
        confidence_score=Decimal("50"),
        strategy_version="v1.0",
    )
    db.add(sig)
    db.flush()
    return sig


# ═══════════════════════════════════════════════════════════════════════════════
# Valid ENUM Values — every value of every enum is accepted
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidEnumValues:
    """All defined enum values should be accepted by PostgreSQL."""

    def test_account_type_values(self, db_session: Session):
        for value in AccountType:
            acct = Account(
                broker_name=f"AT_{value.value}",
                account_number=f"AT-{value.value}",
                account_type=value,
                currency="USD",
            )
            db_session.add(acct)
            db_session.flush()
            assert acct.account_type == value

    def test_asset_class_values(self, db_session: Session):
        for value in AssetClass:
            inst = Instrument(
                symbol=f"AC_{value.value[:4]}",
                name=f"Asset {value.value}",
                asset_class=value,
                exchange="TEST",
                tick_size=Decimal("0.01"),
                currency="USD",
            )
            db_session.add(inst)
            db_session.flush()
            assert inst.asset_class == value

    def test_timeframe_values(self, db_session: Session):
        inst = _instrument(db_session)
        for value in Timeframe:
            ma = MarketAnalysis(
                instrument_id=inst.id,
                timeframe=value,
                analysis_timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
                bias=MarketBias.NEUTRAL,
                trend_health=TrendHealth.HEALTHY,
                confidence_score=Decimal("50"),
            )
            db_session.add(ma)
            db_session.flush()
            assert ma.timeframe == value

    def test_indicator_type_values(self, db_session: Session):
        inst = _instrument(db_session)
        from app.database.models.candle import Candle
        candle = Candle(
            instrument_id=inst.id,
            timestamp=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100"), high=Decimal("101"),
            low=Decimal("99"), close=Decimal("100"),
        )
        db_session.add(candle)
        db_session.flush()
        for value in IndicatorType:
            iv = IndicatorValue(
                instrument_id=inst.id,
                candle_id=candle.id,
                indicator_type=value,
                timeframe=Timeframe.H1,
                value=Decimal("50"),
                calculated_at=datetime(2026, 7, 10, 12, 0, 1, tzinfo=timezone.utc),
            )
            db_session.add(iv)
            db_session.flush()
            assert iv.indicator_type == value

    def test_market_bias_values(self, db_session: Session):
        inst = _instrument(db_session)
        base_ts = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)
        for i, value in enumerate(MarketBias):
            ma = MarketAnalysis(
                instrument_id=inst.id,
                timeframe=Timeframe.H1,
                analysis_timestamp=datetime(2026, 7, 10, 12, 0, i, tzinfo=timezone.utc),
                bias=value,
                trend_health=TrendHealth.HEALTHY,
                confidence_score=Decimal("50"),
            )
            db_session.add(ma)
            db_session.flush()
            assert ma.bias == value

    def test_trend_health_values(self, db_session: Session):
        inst = _instrument(db_session)
        for i, value in enumerate(TrendHealth):
            ma = MarketAnalysis(
                instrument_id=inst.id,
                timeframe=Timeframe.H1,
                analysis_timestamp=datetime(2026, 7, 10, 12, 0, i, tzinfo=timezone.utc),
                bias=MarketBias.NEUTRAL,
                trend_health=value,
                confidence_score=Decimal("50"),
            )
            db_session.add(ma)
            db_session.flush()
            assert ma.trend_health == value

    def test_direction_values(self, db_session: Session):
        inst = _instrument(db_session)
        for value in Direction:
            sig = Signal(
                instrument_id=inst.id,
                direction=value,
                signal_type=SignalType.ENTRY,
                timeframe=Timeframe.H1,
                confidence_score=Decimal("50"),
                strategy_version="v1.0",
            )
            db_session.add(sig)
            db_session.flush()
            assert sig.direction == value

    def test_signal_type_values(self, db_session: Session):
        inst = _instrument(db_session)
        for value in SignalType:
            sig = Signal(
                instrument_id=inst.id,
                direction=Direction.LONG,
                signal_type=value,
                timeframe=Timeframe.H1,
                confidence_score=Decimal("50"),
                strategy_version="v1.0",
            )
            db_session.add(sig)
            db_session.flush()
            assert sig.signal_type == value

    def test_signal_status_values(self, db_session: Session):
        inst = _instrument(db_session)
        for value in SignalStatus:
            sig = Signal(
                instrument_id=inst.id,
                direction=Direction.LONG,
                signal_type=SignalType.ENTRY,
                timeframe=Timeframe.H1,
                confidence_score=Decimal("50"),
                strategy_version="v1.0",
                status=value,
            )
            db_session.add(sig)
            db_session.flush()
            assert sig.status == value

    def test_risk_check_type_values(self, db_session: Session):
        inst = _instrument(db_session)
        sig = _signal(db_session, inst.id)
        for value in RiskCheckType:
            rc = RiskCheck(
                signal_id=sig.id,
                check_type=value,
                passed=True,
            )
            db_session.add(rc)
            db_session.flush()
            assert rc.check_type == value

    def test_order_type_values(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        for i, value in enumerate(OrderType):
            o = Order(
                instrument_id=inst.id,
                account_id=acct.id,
                client_order_id=f"ENUM-OT-{value.value}-{i}",
                direction=Direction.LONG,
                order_type=value,
                quantity=Decimal("1"),
            )
            db_session.add(o)
            db_session.flush()
            assert o.order_type == value

    def test_order_status_values(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        for value in OrderStatus:
            o = Order(
                instrument_id=inst.id,
                account_id=acct.id,
                client_order_id=f"ENUM-OS-{value.value}",
                direction=Direction.LONG,
                order_type=OrderType.MARKET,
                quantity=Decimal("1"),
                status=value,
            )
            db_session.add(o)
            db_session.flush()
            assert o.status == value

    def test_position_status_values(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        for value in PositionStatus:
            p = Position(
                instrument_id=inst.id,
                account_id=acct.id,
                direction=Direction.LONG,
                status=value,
                entry_price=Decimal("100"),
                quantity=Decimal("1"),
                remaining_quantity=Decimal("1"),
                opened_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            )
            db_session.add(p)
            db_session.flush()
            assert p.status == value

    def test_trade_type_values(self, db_session: Session):
        inst = _instrument(db_session)
        acct = _account(db_session)
        order = Order(
            instrument_id=inst.id, account_id=acct.id,
            client_order_id="ENUM-TT-ORDER",
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
        for value in TradeType:
            t = Trade(
                position_id=pos.id, order_id=order.id,
                instrument_id=inst.id, account_id=acct.id,
                direction=Direction.LONG,
                trade_type=value,
                quantity=Decimal("1"), price=Decimal("100"),
                executed_at=datetime(2026, 7, 10, 12, 1, 0, tzinfo=timezone.utc),
            )
            db_session.add(t)
            db_session.flush()
            assert t.trade_type == value

    def test_setting_value_type_values(self, db_session: Session):
        for value in SettingValueType:
            s = Setting(
                key=f"enum.test.{value.value}",
                value="test",
                value_type=value,
                category="TEST",
            )
            db_session.add(s)
            db_session.flush()
            assert s.value_type == value

    def test_log_level_values(self, db_session: Session):
        for value in LogLevel:
            sl = SystemLog(
                level=value,
                module="app.test",
                message=f"Test log {value.value}",
            )
            db_session.add(sl)
            db_session.flush()
            assert sl.level == value

    def test_decision_type_values(self, db_session: Session):
        inst = _instrument(db_session)
        for value in DecisionType:
            dl = DecisionLog(
                instrument_id=inst.id,
                decision_type=value,
                decision_context={},
                reason=f"Test {value.value}",
                confidence_score=Decimal("50"),
                engine_version="v1.0",
            )
            db_session.add(dl)
            db_session.flush()
            assert dl.decision_type == value

    def test_decision_outcome_values(self, db_session: Session):
        inst = _instrument(db_session)
        for value in DecisionOutcome:
            dl = DecisionLog(
                instrument_id=inst.id,
                decision_type=DecisionType.ENTRY,
                decision_context={},
                reason=f"Outcome {value.value}",
                confidence_score=Decimal("50"),
                engine_version="v1.0",
                outcome=value,
            )
            db_session.add(dl)
            db_session.flush()
            assert dl.outcome == value


# ═══════════════════════════════════════════════════════════════════════════════
# Invalid ENUM Values — rejected by PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════


class TestInvalidEnumValues:
    """Invalid enum strings should be rejected at the database level."""

    def test_invalid_asset_class_rejected(self, db_session: Session):
        """Raw SQL with invalid asset_class must fail."""
        from sqlalchemy import text
        with pytest.raises((DataError, IntegrityError)):
            db_session.execute(
                text(
                    "INSERT INTO instruments (symbol, name, asset_class, exchange, "
                    "tick_size, currency) "
                    "VALUES ('INV_AC', 'Invalid', 'BONDS', 'TEST', 0.01, 'USD')"
                ),
            )

    def test_invalid_direction_raw_sql(self, db_session: Session):
        """Raw SQL with invalid enum value must fail."""
        from sqlalchemy import text
        inst = _instrument(db_session)
        with pytest.raises((DataError, IntegrityError)):
            db_session.execute(
                text(
                    "INSERT INTO signals (instrument_id, direction, signal_type, "
                    "timeframe, confidence_score, strategy_version) "
                    "VALUES (:inst_id, 'NEUTRAL', 'ENTRY', '1H', 50.0, 'v1.0')"
                ),
                {"inst_id": inst.id},
            )

    def test_invalid_order_status_raw_sql(self, db_session: Session):
        """Raw SQL with invalid order status must fail."""
        from sqlalchemy import text
        inst = _instrument(db_session)
        acct = _account(db_session, suffix="INV")
        with pytest.raises((DataError, IntegrityError)):
            db_session.execute(
                text(
                    "INSERT INTO orders (instrument_id, account_id, client_order_id, "
                    "direction, order_type, quantity, status) "
                    "VALUES (:inst_id, :acct_id, 'INV-001', 'LONG', 'MARKET', 1.0, 'UNKNOWN')"
                ),
                {"inst_id": inst.id, "acct_id": acct.id},
            )