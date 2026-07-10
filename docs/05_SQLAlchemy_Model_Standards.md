# 05 — SQLAlchemy Model Standards

```text
Document Status : Draft
Phase           : 2B
Version         : 1.0
Last Updated    : 2026-07-10
```

---

## Purpose

This document defines the coding standards for every SQLAlchemy model in the Aegis Trading System. All 15 model files in `backend/app/database/models/` must conform to these rules.

When a new model is written, this document is the single source of truth. If a convention changes, this document changes first — then the models are updated.

---

## 1. Base Class & Imports

### 1.1 Base Class

All models inherit from `app.database.base.Base` (already exists in `backend/app/database/base.py`).

```python
from app.database.base import Base

class Instrument(Base):
    ...
```

### 1.2 SQLAlchemy Import Style

Use SQLAlchemy 2.0 style exclusively. No legacy `Column()` — use `Mapped[]` + `mapped_column()`.

**Allowed imports:**

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
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
```

**Forbidden imports:**

- `from sqlalchemy import Column` — legacy style
- `from sqlalchemy.types import ...` — use mapped_column constructors
- `sqlalchemy.dialects.postgresql import NUMERIC` — use `Numeric(precision, scale)`

---

## 2. Type Annotations

| DB Type | Python Type | SQLAlchemy Column |
|---|---|---|
| `BIGINT` (PK) | `int` | `mapped_column(BigInteger, Identity(), primary_key=True)` |
| `BIGINT` (FK) | `int` | `mapped_column(BigInteger, ForeignKey("table.id"))` |
| `SMALLINT` | `int` | `mapped_column(SmallInteger)` |
| `VARCHAR(n)` | `str` | `mapped_column(String(n))` |
| `TEXT` | `str` | `mapped_column(Text)` |
| `BOOLEAN` | `bool` | `mapped_column(Boolean)` |
| `NUMERIC(p,s)` | `Decimal` | `mapped_column(Numeric(p, s))` |
| `TIMESTAMPTZ` | `datetime` | `mapped_column(DateTime(timezone=True))` |
| `DATE` | `date` | `mapped_column(Date)` |
| `TIME` | `time` | `mapped_column(Time)` |
| `JSONB` | `dict` / `dict | None` | `mapped_column(JSONB)` |
| ENUM | Enum class | `mapped_column(Enum(EnumClass, name="pg_enum_name", create_type=True))` |

### 2.1 Nullable Columns

Use `Optional[...]`:

```python
# Non-nullable
symbol: Mapped[str] = mapped_column(String(50), nullable=False)

# Nullable
stop_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)
```

### 2.2 Never Use `float`

Financial values MUST use `Decimal` with `Numeric`. Never use `Float` or `REAL`.

---

## 3. Column Definition Standards

### 3.1 Primary Keys

```python
id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
```

Every table has a single `id` column named exactly `id`, typed `BIGINT` with `Identity()`.

### 3.2 Foreign Keys

```python
instrument_id: Mapped[int] = mapped_column(
    BigInteger,
    ForeignKey("instruments.id", ondelete="RESTRICT"),
    nullable=False,
)
```

- `ondelete="RESTRICT"` — always, never CASCADE
- Nullable FKs only when documented as optional in `04_Database_Design.md`

### 3.3 Timestamps

**`created_at` (every table):**

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
)
```

**`updated_at` (mutable tables only):**

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
)
```

Mutable tables: `instruments`, `settings`, `orders`, `positions`, `accounts`, `signals`

Immutable tables (no `updated_at`): `candles`, `trades`, `decision_logs`, `indicator_values`, `market_analysis`, `risk_checks`, `market_sessions`, `market_holidays`, `system_logs`

### 3.4 Booleans

```python
is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
```

Use `server_default="true"` (string, not `True`) for PostgreSQL compatibility.

### 3.5 Numeric Columns

Always specify precision and scale:

```python
# Forex price — 5 decimal places
price: Mapped[Decimal] = mapped_column(Numeric(18, 5), nullable=False)

# Crypto volume — 8 decimal places  
volume: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)

# Currency PnL — 2 decimal places
realized_pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)

# Confidence score
confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
```

### 3.6 Enum Columns

```python
asset_class: Mapped[AssetClass] = mapped_column(
    Enum(AssetClass, name="asset_class", create_type=True),
    nullable=False,
)
```

- `create_type=True` — Alembic auto-creates the PG ENUM type on first migration
- The `name` parameter must match the PostgreSQL ENUM type name (lowercase, from `04_Database_Design.md` Section 5)

### 3.7 JSONB Columns

**Critical naming rule:** If the database column is named `metadata`, the Python attribute **must** use a different name. `metadata` is a reserved attribute on SQLAlchemy's `DeclarativeBase` and cannot be used as a column name at the Python level.

Use the pattern `"metadata"` (DB column name) with `metadata_json` (Python attribute name):

```python
# CORRECT — Python name differs from DB column name
metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)

# WRONG — "metadata" is reserved by SQLAlchemy DeclarativeBase
metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # ❌
```

For JSONB columns with non-reserved names, use the standard pattern:

```python
decision_context: Mapped[dict] = mapped_column(JSONB, nullable=False)
```

### 3.8 `server_default` — Not Python `default`

Use `server_default` for DB-level defaults, not Python-side `default=`. This ensures the default is applied at the database level, preventing ORM-vs-DB inconsistency.

```python
# CORRECT
created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# WRONG — do not use Python default for timestamps or DB-constrained defaults
created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
```

---

## 4. Table Configuration

### 4.1 Table Name

```python
__tablename__ = "instruments"
```

Must exactly match the table name in `04_Database_Design.md` Section 4. Always `snake_case` plural.

### 4.2 `__table_args__`

All unique constraints, composite indexes, and FK-column indexes go in `__table_args__`:

```python
__table_args__ = (
    UniqueConstraint("symbol", name="uq_instruments_symbol"),
    Index("ix_instruments_asset_class", "asset_class"),
    Index("ix_instruments_exchange", "exchange"),
)
```

### 4.3 Index Naming Convention

| Pattern | Format | Example |
|---|---|---|
| UNIQUE constraint | `uq_<table>_<columns>` | `uq_instruments_symbol` |
| FK column index | `ix_<table>_<column>` | `ix_candles_instrument_id` |
| Composite index | `ix_<table>_<col1>_<col2>` | `ix_candles_instrument_timestamp` |
| Other indexes | `ix_<table>_<descriptor>` | `ix_signals_status` |

---

## 5. Foreign Keys & Relationships

### 5.1 FK Constraint

Every FK column has:
1. An explicit `ForeignKey` with `ondelete="RESTRICT"`
2. A B-tree index (in `__table_args__`)

### 5.2 Relationship Declaration

Use `back_populates` (not `backref`):

```python
# Parent side (instruments.py)
candles: Mapped[list["Candle"]] = relationship(
    "Candle", back_populates="instrument", lazy="selectin"
)

# Child side (candle.py)
instrument_id: Mapped[int] = mapped_column(
    BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
)
instrument: Mapped["Instrument"] = relationship(
    "Instrument", back_populates="candles", lazy="selectin"
)
```

### 5.3 Lazy Loading Strategy

| Strategy | When |
|---|---|
| `lazy="selectin"` | **Default** — eagerly loads related collections in a separate query, avoiding N+1 for common access patterns |
| `lazy="raise"` | Performance-critical paths where lazy loading should raise an error (used in Phase 6 optimization) |

Do NOT use `lazy="joined"` by default — it creates massive JOIN queries when multiple relationships are loaded.

### 5.4 Nullable Relationship FKs

When the FK column is nullable, the relationship back-ref should use `Optional[...]` where appropriate:

```python
# signal_id is nullable on orders
signal_id: Mapped[Optional[int]] = mapped_column(
    BigInteger, ForeignKey("signals.id", ondelete="RESTRICT"), nullable=True
)
signal: Mapped[Optional["Signal"]] = relationship("Signal", back_populates="orders", lazy="selectin")
```

---

## 6. `__repr__` Policy

Every model must define `__repr__`. Rules:

1. **Minimal** — key identifying fields only
2. **No relationships** — accessing a relationship in repr triggers lazy loads in debug output
3. **Format:** `f"<{ClassName}(id={self.id}, ...)>"`

### Per-Model Repr Examples

| Model | `__repr__` |
|---|---|
| `Instrument` | `f"<Instrument(id={self.id}, symbol='{self.symbol}')>"` |
| `Candle` | `f"<Candle(id={self.id}, instrument_id={self.instrument_id}, timestamp={self.timestamp})>"` |
| `MarketSession` | `f"<MarketSession(id={self.id}, exchange='{self.exchange}', day={self.day_of_week})>"` |
| `MarketHoliday` | `f"<MarketHoliday(id={self.id}, exchange='{self.exchange}', date={self.holiday_date})>"` |
| `IndicatorValue` | `f"<IndicatorValue(id={self.id}, type='{self.indicator_type}', tf='{self.timeframe}')>"` |
| `MarketAnalysis` | `f"<MarketAnalysis(id={self.id}, instrument_id={self.instrument_id}, bias='{self.bias}')>"` |
| `Signal` | `f"<Signal(id={self.id}, direction='{self.direction}', type='{self.signal_type}', status='{self.status}')>"` |
| `RiskCheck` | `f"<RiskCheck(id={self.id}, signal_id={self.signal_id}, check='{self.check_type}', passed={self.passed})>"` |
| `Account` | `f"<Account(id={self.id}, broker='{self.broker_name}', type='{self.account_type}')>"` |
| `Order` | `f"<Order(id={self.id}, client_id='{self.client_order_id}', status='{self.status}')>"` |
| `Position` | `f"<Position(id={self.id}, instrument_id={self.instrument_id}, direction='{self.direction}', status='{self.status}')>"` |
| `Trade` | `f"<Trade(id={self.id}, position_id={self.position_id}, type='{self.trade_type}', price={self.price})>"` |
| `Setting` | `f"<Setting(id={self.id}, key='{self.key}')>"` |
| `SystemLog` | `f"<SystemLog(id={self.id}, level='{self.level}', module='{self.module}')>"` |
| `DecisionLog` | `f"<DecisionLog(id={self.id}, instrument_id={self.instrument_id}, type='{self.decision_type}', outcome='{self.outcome}')>"` |

---

## 7. Immutability Pattern

### 7.1 Mutable Models (have `updated_at`)

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
)
```

### 7.2 Immutable Models (no `updated_at`)

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
)
# No updated_at column
```

Immutable models are defined in Section 3.3 above.

---

## 8. Model File Template

Every model file follows this exact structure:

```python
"""
Model: <TableName> — <one-line description of what this table stores>

References:
    04_Database_Design.md — Section 4.X <TableName>
"""
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import (
    # Import only the enums this model uses
)


class ModelName(Base):
    """<One-line description>"""

    __tablename__ = "<table_name>"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint("col1", "col2", name="uq_table_cols"),
        Index("ix_table_fkcol", "fk_column"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    # Foreign keys
    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parents.id", ondelete="RESTRICT"), nullable=False
    )

    # Scalar columns
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    parent: Mapped["Parent"] = relationship(
        "Parent", back_populates="children", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"<ModelName(id={self.id}, name='{self.name}')>"
```

---

## 9. Enum Mapping Reference

| Python Enum Class | PostgreSQL ENUM Name | Used By (Table.Column) |
|---|---|---|
| `AccountType` | `account_type` | `accounts.account_type` |
| `AssetClass` | `asset_class` | `instruments.asset_class` |
| `Timeframe` | `timeframe` | `indicator_values.timeframe`, `market_analysis.timeframe`, `signals.timeframe` |
| `IndicatorType` | `indicator_type` | `indicator_values.indicator_type` |
| `MarketBias` | `market_bias` | `market_analysis.bias` |
| `TrendHealth` | `trend_health` | `market_analysis.trend_health` |
| `Direction` | `direction` | `signals.direction`, `orders.direction`, `positions.direction`, `trades.direction` |
| `SignalType` | `signal_type` | `signals.signal_type` |
| `SignalStatus` | `signal_status` | `signals.status` |
| `RiskCheckType` | `risk_check_type` | `risk_checks.check_type` |
| `OrderType` | `order_type` | `orders.order_type` |
| `OrderStatus` | `order_status` | `orders.status` |
| `PositionStatus` | `position_status` | `positions.status` |
| `TradeType` | `trade_type` | `trades.trade_type` |
| `SettingValueType` | `setting_value_type` | `settings.value_type` |
| `LogLevel` | `log_level` | `system_logs.level` |
| `DecisionType` | `decision_type` | `decision_logs.decision_type` |
| `DecisionOutcome` | `decision_outcome` | `decision_logs.outcome` |

**Note:** `Direction` and `SignalType`/`TradeType`/`DecisionType` share overlapping value sets (`LONG`/`SHORT`, `ENTRY`/`EXIT`/`PARTIAL_EXIT`/`RE_ENTRY`) but are **separate PostgreSQL ENUM types** because they represent different concepts and may diverge in future versions. Each gets its own PG ENUM.

---

## 10. Dependency Order

Models must be written and imported in this order to avoid circular imports:

```
Phase 2B.1  — enums.py                 (no dependencies)
Phase 2B.2  — instrument.py            (no FK dependencies on other models)
Phase 2B.3  — candle.py                (FK → instruments)
Phase 2B.4  — market_session.py        (standalone)
Phase 2B.5  — market_holiday.py        (standalone)
Phase 2B.6  — indicator_value.py       (FK → instruments, candles)
Phase 2B.7  — market_analysis.py       (FK → instruments)
Phase 2B.8  — signal.py                (FK → instruments)
Phase 2B.9  — risk_check.py            (FK → signals)
Phase 2B.10 — account.py               (standalone)
Phase 2B.11 — order.py                 (FK → signals, instruments, accounts)
Phase 2B.12 — position.py              (FK → instruments, accounts)
Phase 2B.13 — trade.py                 (FK → positions, orders, instruments, accounts)
Phase 2B.14 — setting.py               (standalone)
Phase 2B.15 — system_log.py            (standalone)
Phase 2B.16 — decision_log.py          (FK → signals, instruments)
Phase 2B.17 — models/__init__.py       (imports all 15 models)
```

---

## 11. What NOT to Include in Models

- ❌ No `__init__` methods — SQLAlchemy provides these
- ❌ No `@property` for simple column access — use the column directly
- ❌ No business logic — models are pure data descriptors
- ❌ No `default=datetime.utcnow` — use `server_default=func.now()`
- ❌ No `backref` — use `back_populates` exclusively
- ❌ No `ForeignKey` without explicit index
- ❌ No `table` argument on `relationship` — always reference the class name string

---

END OF DOCUMENT