# 04 — Database Design

```text
Document Status : Approved
Phase           : 2A
Version         : 1.0
Last Updated    : 2026-07-10
```

---

## Database Version: 1.0

Future schema updates will increment this version (1.1, 1.2, 2.0, etc.).

---

# Purpose

This document is the single blueprint for every database table in the Aegis Trading System.

Once approved, SQLAlchemy models (Phase 2B), Alembic migrations (Phase 2C), and database tests (Phase 2D) are implemented directly from this document.

**No model is written before this document is marked Approved.**

---

# 1. Design Principles

These principles explain *why* the schema looks the way it does.

## 1.1 Simplicity Over Premature Optimization

The schema is normalized and straightforward. We do not pre-partition, pre-shard, or add complex denormalization unless a proven performance need exists. Trading correctness comes first; optimization comes later when real query patterns are known.

## 1.2 Immutable Historical Trading Data

Candles, trades, and decision logs are write-once records. They are never updated or deleted. This guarantees a complete audit trail. Only mutable entities (instruments, settings, orders, positions) have an `updated_at` column.

## 1.3 UTC as the Canonical Time Standard

Every timestamp is stored as `TIMESTAMP WITH TIME ZONE` in UTC. The application converts to UTC before writing. The frontend converts to the user's local timezone for display only. No local times are stored in the database.

## 1.4 Normalize Only Where It Improves Clarity

We normalize to avoid data duplication and keep relationships explicit. We do not over-normalize to the point where simple queries require five joins. Analytical metadata that is complex and variable (indicator parameters, decision context) is stored as `JSONB`.

## 1.5 Designed for One Broker Initially, with Future Expansion

The schema includes an `accounts` table from the start, supporting multiple accounts (paper, demo, live) and multiple brokers. In Version 1, a single default account is used. When Phase 8 introduces a concrete broker, new accounts can be added without schema changes.

## 1.6 Accuracy > Speed > Profit

Prices and quantities use `NUMERIC` — never floating point. Financial calculations must be exact. Performance is secondary to correctness for stored values.

---

# 2. Database Conventions

These conventions are locked for Phase 2 and should not change without an architecture review.

## 2.1 Technology

| Item | Decision |
|---|---|
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x |
| Migration Tool | Alembic |
| Driver | psycopg3 (`psycopg[binary]>=3.2`) |
| Connection URL | `postgresql+psycopg://...` |

## 2.2 Naming

| Item | Convention | Example |
|---|---|---|
| Table names | `snake_case`, plural | `instruments`, `candles`, `market_sessions` |
| Column names | `snake_case` | `instrument_id`, `created_at` |
| Foreign keys | `<singular_entity>_id` | `instrument_id`, `signal_id` |
| Index names | `ix_<table>_<columns>` | `ix_candles_instrument_id` |
| Unique constraints | `uq_<table>_<columns>` | `uq_instruments_symbol` |
| Enum types | `UPPER_SNAKE` values | `LONG`, `SHORT`, `MARKET`, `LIMIT` |

## 2.3 Primary Keys

| Item | Decision |
|---|---|
| Type | `BIGINT` auto-increment |
| SQLAlchemy | `BigInteger` with `Identity()` |
| Name | Always `id` |
| Surrogate | Yes — no natural keys as PKs |

Natural keys (e.g., `symbol` on `instruments`) are enforced with `UNIQUE` constraints, not as primary keys.

## 2.4 Timestamps

| Item | Decision |
|---|---|
| Type | `TIMESTAMP WITH TIME ZONE` |
| SQLAlchemy | `DateTime(timezone=True)` |
| Canonical | UTC — always |
| `created_at` | Every table — set once, never updated |
| `updated_at` | Only on mutable tables (see below) |

### `updated_at` Policy

| Table | `updated_at`? | Reason |
|---|---|---|
| `instruments` | ✅ | Tick size, contract size, active status can change |
| `settings` | ✅ | Configuration values change |
| `orders` | ✅ | Order status changes (PENDING → FILLED) |
| `positions` | ✅ | PnL, stop loss, remaining quantity change |
| `accounts` | ✅ | Balance, active status, default flag can change |
| `signals` | ✅ | Signal status changes (PENDING → APPROVED → EXECUTED) |
| `candles` | ❌ | Immutable market data |
| `trades` | ❌ | Immutable execution record |
| `decision_logs` | ❌ | Immutable audit trail |
| `indicator_values` | ❌ | Immutable calculation result |
| `market_analysis` | ❌ | Immutable analysis snapshot |
| `risk_checks` | ❌ | Immutable validation record |
| `market_sessions` | ❌ | Rarely changes; recreate if needed |
| `market_holidays` | ❌ | Annual calendar; recreate if needed |
| `system_logs` | ❌ | Immutable log entry |

## 2.5 Numeric Precision

Prices and quantities use `NUMERIC` with precision appropriate to the asset type. Precision is defined per column — not globally.

| Use Case | Type | Rationale |
|---|---|---|
| Forex prices | `NUMERIC(18,5)` | 5 decimal places (e.g., 1.08542) |
| Crypto prices | `NUMERIC(18,8)` | 8 decimal places (e.g., 0.00001234) |
| Index/stock prices | `NUMERIC(18,4)` | 4 decimal places |
| Quantities | `NUMERIC(18,8)` | High precision for fractional shares/crypto |
| PnL / account balance | `NUMERIC(18,2)` | 2 decimal places (currency) |
| Confidence score | `NUMERIC(5,2)` | 0.00 to 100.00 |
| Volume | `NUMERIC(20,8)` | Large values, high precision |

**Rule:** Never use `FLOAT` or `REAL` for financial data.

## 2.6 Enums

| Item | Decision |
|---|---|
| Python side | `class FooEnum(str, Enum)` |
| PostgreSQL side | Native `ENUM` type |
| Migration | Created via Alembic `op.create_enum()` |
| Storage | Stored as native PG enum, not VARCHAR |

## 2.7 Foreign Keys

| Item | Decision |
|---|---|
| Explicit | Every FK has an explicit `ForeignKey` constraint |
| Index | Every FK column has a B-tree index |
| ON DELETE | `RESTRICT` — never cascade-delete trading data |
| Nullable FKs | Allowed only when the relationship is optional (documented per table) |

## 2.8 Soft Delete

**No soft deletes.** Trading history is immutable. If an instrument is deactivated, set `is_active = FALSE`. Never delete a row that has financial or audit significance.

## 2.9 JSONB Usage

`JSONB` is used for:

- `indicator_values.metadata` — multi-value indicators (e.g., MACD signal + histogram)
- `market_analysis.metadata` — detailed analysis breakdown
- `signals.metadata` — full decision context
- `decision_logs.decision_context` — complete audit snapshot
- `system_logs.metadata` — structured log context

`JSONB` is **not** used for:

- Anything that needs indexing for frequent queries
- Anything that could be a normal column
- Financial values (prices, quantities)

## 2.10 Indexing Strategy

| Index Type | Where |
|---|---|
| B-tree (default) | All FK columns, all UNIQUE constraints |
| Composite B-tree | Common query patterns (see per-table definitions) |
| GIN | `JSONB` columns that are queried by key |

Indexes are defined explicitly per table in Section 4.

---

# 3. Entity Relationship Diagram

```
                    ┌──────────────┐
                    │  instruments  │
                    └──────┬───────┘
                           │
           ┌───────────────┼────────────────────────┐
           │               │                        │
           ▼               ▼                        ▼
    ┌──────────┐   ┌─────────────────┐     ┌──────────────┐
    │  candles  │   │ market_analysis  │     │   signals    │
    └─────┬────┘   └─────────────────┘     └──────┬───────┘
          │                                       │
          ▼                              ┌────────┼────────┐
    ┌──────────────────┐                │        │        │
    │ indicator_values  │                ▼        ▼        ▼
    └──────────────────┘         ┌──────────┐ ┌──────────────┐ ┌──────────────┐
                                 │risk_checks│ │   orders     │ │decision_logs │
                                 └──────────┘ └──────┬───────┘ └──────────────┘
                                                     │
                                                     ▼
                                               ┌──────────┐
                                               │  trades   │
                                               └─────┬────┘
                                                     │
                                                     ▼
                                               ┌───────────┐
                                               │ positions  │
                                               └───────────┘

    ┌───────────┐
    │  accounts  │──→ orders, positions, trades (account_id)
    └───────────┘

    Standalone tables (no FK relationships):
    ┌─────────────────┐  ┌──────────────────┐  ┌──────────┐  ┌─────────────┐
    │ market_sessions  │  │ market_holidays   │  │ settings  │  │ system_logs  │
    └─────────────────┘  └──────────────────┘  └──────────┘  └─────────────┘
```

### Relationship Summary

| Parent | Child | Cardinality | FK Column |
|---|---|---|---|
| `instruments` | `candles` | 1:N | `candles.instrument_id` |
| `instruments` | `market_analysis` | 1:N | `market_analysis.instrument_id` |
| `instruments` | `signals` | 1:N | `signals.instrument_id` |
| `instruments` | `positions` | 1:N | `positions.instrument_id` |
| `instruments` | `decision_logs` | 1:N | `decision_logs.instrument_id` |
| `candles` | `indicator_values` | 1:N | `indicator_values.candle_id` |
| `signals` | `risk_checks` | 1:N | `risk_checks.signal_id` |
| `signals` | `orders` | 1:N | `orders.signal_id` (nullable) |
| `signals` | `decision_logs` | 1:N | `decision_logs.signal_id` (nullable) |
| `orders` | `trades` | 1:N | `trades.order_id` |
| `accounts` | `orders` | 1:N | `orders.account_id` |
| `accounts` | `positions` | 1:N | `positions.account_id` |
| `accounts` | `trades` | 1:N | `trades.account_id` |
| `positions` | `trades` | 1:N | `trades.position_id` |

---

# 4. Table Definitions

Tables are grouped by dependency. Review each group before proceeding to the next.

---

## Group 1 — Market Data Foundation

### 4.1 `instruments`

Tradable instruments. The root entity — nearly every other table references this.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `symbol` | `VARCHAR(50)` | UNIQUE, NOT NULL | Instrument symbol (e.g., `SPX500`, `EURUSD`, `BTCUSDT`) |
| `name` | `VARCHAR(200)` | NOT NULL | Human-readable name (e.g., `S&P 500 Index`) |
| `asset_class` | `ENUM` | NOT NULL | `INDEX`, `FOREX`, `COMMODITY`, `CRYPTO`, `STOCK` |
| `exchange` | `VARCHAR(50)` | NOT NULL | Exchange or venue (e.g., `CME`, `FOREX`, `BINANCE`) |
| `tick_size` | `NUMERIC(18,8)` | NOT NULL | Minimum price increment |
| `contract_size` | `NUMERIC(18,8)` | NOT NULL, DEFAULT 1.0 | Size of one contract/unit |
| `currency` | `VARCHAR(10)` | NOT NULL | Quote currency (e.g., `USD`, `EUR`) |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Soft-deactivation flag |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last modification |

**Indexes:**
- `uq_instruments_symbol` — UNIQUE on `symbol`
- `ix_instruments_asset_class` — on `asset_class`
- `ix_instruments_exchange` — on `exchange`

---

### 4.2 `candles`

OHLCV market data. Stores **1-minute candles only** — this is the canonical source data. Higher timeframes (5M, 15M, 1H, 4H) are generated in-memory by the Market Data Engine (Phase 3) and are not stored in this table.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `timestamp` | `TIMESTAMPTZ` | NOT NULL | Candle open time (UTC) |
| `open` | `NUMERIC(18,8)` | NOT NULL | Open price |
| `high` | `NUMERIC(18,8)` | NOT NULL | High price |
| `low` | `NUMERIC(18,8)` | NOT NULL | Low price |
| `close` | `NUMERIC(18,8)` | NOT NULL | Close price |
| `volume` | `NUMERIC(20,8)` | NOT NULL, DEFAULT 0 | Trade volume |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Constraints:**
- `uq_candles_instrument_timestamp` — UNIQUE on `(instrument_id, timestamp)`

**Indexes:**
- `ix_candles_instrument_id` — on `instrument_id`
- `ix_candles_instrument_timestamp` — composite on `(instrument_id, timestamp)`

**Note:** The unique constraint prevents duplicate candles for the same instrument at the same timestamp. The composite index optimizes the most common query: "get candles for instrument X, ordered by timestamp."

---

### 4.3 `market_sessions`

Defines regular trading hours per exchange per day of week.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `exchange` | `VARCHAR(50)` | NOT NULL | Exchange name (e.g., `CME`, `FOREX`) |
| `day_of_week` | `SMALLINT` | NOT NULL | 0=Sunday … 6=Saturday |
| `open_time` | `TIME` | NOT NULL | Session open time (in session timezone) |
| `close_time` | `TIME` | NOT NULL | Session close time (in session timezone) |
| `timezone` | `VARCHAR(50)` | NOT NULL | IANA timezone (e.g., `America/New_York`) |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Whether this session is current |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Constraints:**
- `uq_market_sessions_exchange_day` — UNIQUE on `(exchange, day_of_week)`

**Indexes:**
- `ix_market_sessions_exchange` — on `exchange`

---

### 4.4 `market_holidays`

Holiday calendar per exchange. Overrides `market_sessions` on specific dates.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `exchange` | `VARCHAR(50)` | NOT NULL | Exchange name |
| `holiday_date` | `DATE` | NOT NULL | Date of the holiday |
| `name` | `VARCHAR(200)` | NOT NULL | Holiday name (e.g., `Independence Day`) |
| `is_full_day` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Full day closure |
| `early_close_time` | `TIME` | NULL | Early close time for half-days (NULL if full day) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Constraints:**
- `uq_market_holidays_exchange_date` — UNIQUE on `(exchange, holiday_date)`

**Indexes:**
- `ix_market_holidays_exchange` — on `exchange`
- `ix_market_holidays_holiday_date` — on `holiday_date`

---

### ⏸ Review Checkpoint — Group 1

Before proceeding to Group 2, confirm:
- [ ] `instruments` columns and asset class enum are correct
- [ ] `candles` unique constraint prevents duplicates correctly
- [ ] `market_sessions` timezone approach is acceptable
- [ ] `market_holidays` half-day handling is sufficient

---

## Group 2 — Analysis Layer

### 4.5 `indicator_values`

Stores computed indicator values per candle. One row per indicator per candle per timeframe.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `candle_id` | `BIGINT` | FK → `candles.id`, NOT NULL | Which candle this was calculated at |
| `indicator_type` | `ENUM` | NOT NULL | `ATR`, `EMA`, `MACD`, `RSI`, `CISD`, `MOMENTUM` |
| `timeframe` | `ENUM` | NOT NULL | `1M`, `5M`, `15M`, `1H`, `4H` |
| `value` | `NUMERIC(18,8)` | NOT NULL | Primary indicator value |
| `metadata` | `JSONB` | NULL | Multi-value indicator data (e.g., MACD: `{signal: 0.5, histogram: 0.2}`) |
| `calculated_at` | `TIMESTAMPTZ` | NOT NULL | When the indicator was computed |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Constraints:**
- `uq_indicator_values_instrument_candle_type_tf` — UNIQUE on `(instrument_id, candle_id, indicator_type, timeframe)`

**Indexes:**
- `ix_indicator_values_instrument_id` — on `instrument_id`
- `ix_indicator_values_candle_id` — on `candle_id`
- `ix_indicator_values_indicator_type` — on `indicator_type`

---

### 4.6 `market_analysis`

Multi-timeframe analysis snapshots. One row per instrument per timeframe per analysis timestamp.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `timeframe` | `ENUM` | NOT NULL | `1M`, `5M`, `15M`, `1H`, `4H` |
| `analysis_timestamp` | `TIMESTAMPTZ` | NOT NULL | When the analysis was performed |
| `bias` | `ENUM` | NOT NULL | `BULLISH`, `BEARISH`, `NEUTRAL` |
| `trend_health` | `ENUM` | NOT NULL | `HEALTHY`, `WEAK`, `BROKEN` |
| `confidence_score` | `NUMERIC(5,2)` | NOT NULL | 0.00 to 100.00 |
| `metadata` | `JSONB` | NULL | Detailed breakdown (indicator values, patterns detected) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Constraints:**
- `uq_market_analysis_instrument_tf_timestamp` — UNIQUE on `(instrument_id, timeframe, analysis_timestamp)`

**Indexes:**
- `ix_market_analysis_instrument_id` — on `instrument_id`
- `ix_market_analysis_instrument_tf_timestamp` — composite on `(instrument_id, timeframe, analysis_timestamp)`

---

### 4.7 `signals`

Trading signals generated by the Strategy Engine. A signal is the output of the decision process before risk checks and execution.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `direction` | `ENUM` | NOT NULL | `LONG`, `SHORT` |
| `signal_type` | `ENUM` | NOT NULL | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY` |
| `timeframe` | `ENUM` | NOT NULL | Primary timeframe of the signal |
| `entry_price` | `NUMERIC(18,8)` | NULL | Suggested entry price (NULL for market orders) |
| `stop_loss` | `NUMERIC(18,8)` | NULL | Suggested stop loss price |
| `take_profit` | `NUMERIC(18,8)` | NULL | Suggested take profit price |
| `confidence_score` | `NUMERIC(5,2)` | NOT NULL | 0.00 to 100.00 |
| `strategy_version` | `VARCHAR(20)` | NOT NULL | Strategy version that generated this signal (e.g., `v1.0`, `strategy_v3`) |
| `status` | `ENUM` | NOT NULL, DEFAULT `PENDING` | `PENDING`, `APPROVED`, `REJECTED`, `EXECUTED`, `EXPIRED`, `CANCELLED` |
| `expires_at` | `TIMESTAMPTZ` | NULL | When the signal becomes invalid (NULL = never expires) |
| `metadata` | `JSONB` | NULL | Full decision context (indicators, analysis references) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last status change |

**Indexes:**
- `ix_signals_instrument_id` — on `instrument_id`
- `ix_signals_status` — on `status`
- `ix_signals_created_at` — on `created_at`
- `ix_signals_expires_at` — on `expires_at`

---

### ⏸ Review Checkpoint — Group 2

Before proceeding to Group 3, confirm:
- [ ] `indicator_values.metadata` JSONB structure for multi-value indicators is acceptable
- [ ] `market_analysis` bias and trend_health enums cover all needed states
- [ ] `signals` status lifecycle (PENDING → APPROVED/REJECTED → EXECUTED/EXPIRED/CANCELLED) is correct
- [ ] `signals.entry_price` being nullable for market orders is acceptable

---

## Group 3 — Trading Layer

### 4.8 `risk_checks`

Pre-trade risk validation records. One signal can have multiple risk checks (position size, stop loss distance, exposure limit, etc.).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `signal_id` | `BIGINT` | FK → `signals.id`, NOT NULL | Which signal is being checked |
| `check_type` | `ENUM` | NOT NULL | `POSITION_SIZE`, `STOP_LOSS_DISTANCE`, `EXPOSURE_LIMIT`, `MAX_DRAWDOWN`, `MAX_POSITIONS`, `DAILY_LOSS_LIMIT` |
| `passed` | `BOOLEAN` | NOT NULL | Whether the check passed |
| `check_value` | `NUMERIC(18,8)` | NULL | The actual value that was checked |
| `threshold_value` | `NUMERIC(18,8)` | NULL | The limit/threshold for this check |
| `message` | `TEXT` | NULL | Human-readable explanation (especially on failure) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Indexes:**
- `ix_risk_checks_signal_id` — on `signal_id`
- `ix_risk_checks_check_type` — on `check_type`
- `ix_risk_checks_passed` — on `passed`

---

### 4.9 `accounts`

Trading accounts. Supports multiple account types (paper, demo, live) and multiple brokers. In Version 1, a single default account is used.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `broker_name` | `VARCHAR(100)` | NOT NULL | Broker name (e.g., `PaperBroker`, `InteractiveBrokers`, `Alpaca`) |
| `account_number` | `VARCHAR(100)` | NOT NULL | Broker-assigned account number |
| `account_type` | `ENUM` | NOT NULL | `PAPER`, `DEMO`, `LIVE` |
| `currency` | `VARCHAR(10)` | NOT NULL | Account base currency (e.g., `USD`, `EUR`) |
| `balance` | `NUMERIC(18,2)` | NOT NULL, DEFAULT 0 | Current account balance |
| `is_default` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | Whether this is the default account |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Whether this account is active |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last modification |

**Constraints:**
- `uq_accounts_broker_account_number` — UNIQUE on `(broker_name, account_number)`

**Indexes:**
- `ix_accounts_account_type` — on `account_type`
- `ix_accounts_is_active` — on `is_active`

---

### 4.10 `orders`

Order lifecycle. An order is submitted to the broker after a signal passes risk checks.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `signal_id` | `BIGINT` | FK → `signals.id`, NULL | Originating signal (NULL for manual orders) |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `account_id` | `BIGINT` | FK → `accounts.id`, NOT NULL | Which account |
| `client_order_id` | `VARCHAR(50)` | UNIQUE, NOT NULL | Internal ATS order ID (e.g., `AGS-20260710-000123`) |
| `broker_order_id` | `VARCHAR(100)` | NULL | ID assigned by the broker |
| `direction` | `ENUM` | NOT NULL | `LONG`, `SHORT` |
| `order_type` | `ENUM` | NOT NULL | `MARKET`, `LIMIT`, `STOP` |
| `quantity` | `NUMERIC(18,8)` | NOT NULL | Requested quantity |
| `price` | `NUMERIC(18,8)` | NULL | Limit price (required for LIMIT orders) |
| `stop_price` | `NUMERIC(18,8)` | NULL | Stop price (required for STOP orders) |
| `status` | `ENUM` | NOT NULL, DEFAULT `PENDING` | `PENDING`, `FILLED`, `PARTIALLY_FILLED`, `CANCELLED`, `REJECTED` |
| `filled_price` | `NUMERIC(18,8)` | NULL | Average fill price |
| `filled_quantity` | `NUMERIC(18,8)` | NULL | Total filled quantity |
| `submitted_at` | `TIMESTAMPTZ` | NULL | When order was sent to broker |
| `filled_at` | `TIMESTAMPTZ` | NULL | When order was filled |
| `cancelled_at` | `TIMESTAMPTZ` | NULL | When order was cancelled |
| `broker_message` | `TEXT` | NULL | Broker status message (e.g., rejection reason: "Invalid stop distance", "Market closed") |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last status change |

**Constraints:**
- `uq_orders_client_order_id` — UNIQUE on `client_order_id`

**Indexes:**
- `ix_orders_account_id` — on `account_id`
- `ix_orders_signal_id` — on `signal_id`
- `ix_orders_instrument_id` — on `instrument_id`
- `ix_orders_status` — on `status`
- `ix_orders_broker_order_id` — on `broker_order_id`

---

### 4.11 `positions`

Open and closed position tracking. A position is the aggregate of one or more trades over its lifecycle.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `account_id` | `BIGINT` | FK → `accounts.id`, NOT NULL | Which account |
| `direction` | `ENUM` | NOT NULL | `LONG`, `SHORT` |
| `status` | `ENUM` | NOT NULL, DEFAULT `OPEN` | `OPEN`, `CLOSED`, `PARTIALLY_CLOSED` |
| `entry_price` | `NUMERIC(18,8)` | NOT NULL | Average entry price |
| `quantity` | `NUMERIC(18,8)` | NOT NULL | Original position quantity |
| `remaining_quantity` | `NUMERIC(18,8)` | NOT NULL | Quantity still open |
| `stop_loss` | `NUMERIC(18,8)` | NULL | Current stop loss price (may trail) |
| `take_profit` | `NUMERIC(18,8)` | NULL | Current take profit price |
| `unrealized_pnl` | `NUMERIC(18,2)` | NULL | PnL if position were closed at current price |
| `realized_pnl` | `NUMERIC(18,2)` | NULL | PnL from partial closes |
| `opened_at` | `TIMESTAMPTZ` | NOT NULL | When the position was opened |
| `closed_at` | `TIMESTAMPTZ` | NULL | When the position was fully closed |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last modification |

**Indexes:**
- `ix_positions_account_id` — on `account_id`
- `ix_positions_instrument_id` — on `instrument_id`
- `ix_positions_status` — on `status`
- `ix_positions_opened_at` — on `opened_at`

---

### 4.12 `trades`

Completed execution records. Each trade represents a fill — an entry, partial exit, full exit, or re-entry within a position.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `position_id` | `BIGINT` | FK → `positions.id`, NOT NULL | Which position this trade belongs to |
| `order_id` | `BIGINT` | FK → `orders.id`, NOT NULL | Which order generated this fill |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `account_id` | `BIGINT` | FK → `accounts.id`, NOT NULL | Which account |
| `direction` | `ENUM` | NOT NULL | `LONG`, `SHORT` |
| `trade_type` | `ENUM` | NOT NULL | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY` |
| `quantity` | `NUMERIC(18,8)` | NOT NULL | Filled quantity |
| `price` | `NUMERIC(18,8)` | NOT NULL | Fill price |
| `pnl` | `NUMERIC(18,2)` | NULL | Realized PnL for this trade (NULL for entries) |
| `commission` | `NUMERIC(18,2)` | NULL, DEFAULT 0 | Commission/fee paid |
| `slippage` | `NUMERIC(18,8)` | NULL | Difference between expected and executed price |
| `executed_at` | `TIMESTAMPTZ` | NOT NULL | Execution timestamp |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Indexes:**
- `ix_trades_account_id` — on `account_id`
- `ix_trades_position_id` — on `position_id`
- `ix_trades_order_id` — on `order_id`
- `ix_trades_instrument_id` — on `instrument_id`
- `ix_trades_executed_at` — on `executed_at`

---

### ⏸ Review Checkpoint — Group 3

Before proceeding to Group 4, confirm:
- [ ] `accounts` table supports paper/demo/live and multi-broker
- [ ] `risk_checks` check types cover all risk validations needed
- [ ] `orders.signal_id` being nullable for manual orders is acceptable
- [ ] `positions` PnL columns (`unrealized_pnl`, `realized_pnl`) with `NUMERIC(18,2)` is correct
- [ ] `trades` relationship to both `positions` and `orders` is correct
- [ ] `trades.pnl` being NULL for entries (not 0) is acceptable

---

## Group 4 — System Layer

### 4.13 `settings`

Key-value system configuration stored in the database. For settings that can be changed at runtime without restarting the application.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `key` | `VARCHAR(100)` | UNIQUE, NOT NULL | Setting key (e.g., `risk.max_position_size`) |
| `value` | `TEXT` | NOT NULL | Setting value (stored as text, interpreted by `value_type`) |
| `value_type` | `ENUM` | NOT NULL | `STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `JSON` |
| `description` | `TEXT` | NULL | Human-readable explanation |
| `category` | `VARCHAR(50)` | NOT NULL | Grouping (e.g., `RISK`, `STRATEGY`, `SYSTEM`) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last modification |

**Constraints:**
- `uq_settings_key` — UNIQUE on `key`

**Indexes:**
- `ix_settings_category` — on `category`

---

### 4.14 `system_logs`

Structured application logging. For system events, errors, and operational diagnostics. This is separate from `decision_logs` which captures trading decisions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `level` | `ENUM` | NOT NULL | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `module` | `VARCHAR(100)` | NOT NULL | Source module (e.g., `app.market.data_provider`) |
| `message` | `TEXT` | NOT NULL | Log message |
| `metadata` | `JSONB` | NULL | Structured context (exception details, request IDs, etc.) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Indexes:**
- `ix_system_logs_level` — on `level`
- `ix_system_logs_module` — on `module`
- `ix_system_logs_created_at` — on `created_at`

**Note:** This table may grow rapidly. A future phase may add table partitioning by date. For Phase 2, a simple structure is sufficient.

---

### 4.15 `decision_logs`

The complete audit trail of every trading decision. This is the foundation for Phase 13 (Decision Journal & Intelligence Monitoring). Every decision — whether it resulted in a trade or not — is recorded here.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGINT` | PK, auto-increment | Surrogate key |
| `signal_id` | `BIGINT` | FK → `signals.id`, NULL | Associated signal (NULL for decisions that did not produce a signal) |
| `instrument_id` | `BIGINT` | FK → `instruments.id`, NOT NULL | Which instrument |
| `decision_type` | `ENUM` | NOT NULL | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY`, `REJECT`, `CANCEL` |
| `decision_context` | `JSONB` | NOT NULL | Full context snapshot (indicators, analysis, risk check results, market state) |
| `reason` | `TEXT` | NOT NULL | Human-readable explanation of the decision |
| `confidence_score` | `NUMERIC(5,2)` | NOT NULL | 0.00 to 100.00 |
| `engine_version` | `VARCHAR(20)` | NOT NULL | Strategy engine version (e.g., `v1.0`, `strategy_v3`) — identifies which strategy produced this decision |
| `outcome` | `ENUM` | NOT NULL, DEFAULT `PENDING` | `PENDING`, `SUCCESS`, `FAILURE`, `EXPIRED` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Record creation |

**Indexes:**
- `ix_decision_logs_signal_id` — on `signal_id`
- `ix_decision_logs_instrument_id` — on `instrument_id`
- `ix_decision_logs_decision_type` — on `decision_type`
- `ix_decision_logs_created_at` — on `created_at`

**Note:** `decision_context` is the most important column in the system for explainability. It should capture enough information to reconstruct *why* a decision was made, even years later. The exact JSONB schema will be defined in Phase 5 (Strategy Engine) and Phase 13 (Decision Journal).

---

### ⏸ Review Checkpoint — Group 4

Before marking this document Approved, confirm:
- [ ] `settings` key-value approach with `value_type` enum is sufficient
- [ ] `system_logs` structure is adequate (or if a separate logging solution like Loki/ELK is preferred)
- [ ] `decision_logs.decision_context` JSONB approach is acceptable for the audit trail
- [ ] `decision_logs.outcome` enum covers all possible outcomes

---

# 5. Enum Type Reference

All enums used across the schema, consolidated for implementation reference.

| Enum Name | Values | Used By |
|---|---|---|
| `AccountType` | `PAPER`, `DEMO`, `LIVE` | `accounts.account_type` |
| `AssetClass` | `INDEX`, `FOREX`, `COMMODITY`, `CRYPTO`, `STOCK` | `instruments.asset_class` |
| `Timeframe` | `1M`, `5M`, `15M`, `1H`, `4H` | `indicator_values`, `market_analysis`, `signals` |
| `IndicatorType` | `ATR`, `EMA`, `MACD`, `RSI`, `CISD`, `MOMENTUM` | `indicator_values.indicator_type` |
| `MarketBias` | `BULLISH`, `BEARISH`, `NEUTRAL` | `market_analysis.bias` |
| `TrendHealth` | `HEALTHY`, `WEAK`, `BROKEN` | `market_analysis.trend_health` |
| `Direction` | `LONG`, `SHORT` | `signals`, `orders`, `positions`, `trades` |
| `SignalType` | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY` | `signals.signal_type` |
| `SignalStatus` | `PENDING`, `APPROVED`, `REJECTED`, `EXECUTED`, `EXPIRED`, `CANCELLED` | `signals.status` |
| `RiskCheckType` | `POSITION_SIZE`, `STOP_LOSS_DISTANCE`, `EXPOSURE_LIMIT`, `MAX_DRAWDOWN`, `MAX_POSITIONS`, `DAILY_LOSS_LIMIT` | `risk_checks.check_type` |
| `OrderType` | `MARKET`, `LIMIT`, `STOP` | `orders.order_type` |
| `OrderStatus` | `PENDING`, `FILLED`, `PARTIALLY_FILLED`, `CANCELLED`, `REJECTED` | `orders.status` |
| `PositionStatus` | `OPEN`, `CLOSED`, `PARTIALLY_CLOSED` | `positions.status` |
| `TradeType` | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY` | `trades.trade_type` |
| `SettingValueType` | `STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `JSON` | `settings.value_type` |
| `LogLevel` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `system_logs.level` |
| `DecisionType` | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY`, `REJECT`, `CANCEL` | `decision_logs.decision_type` |
| `DecisionOutcome` | `PENDING`, `SUCCESS`, `FAILURE`, `EXPIRED` | `decision_logs.outcome` |

---

# 6. Implementation Notes

## 6.1 File Structure (Phase 2B)

```text
backend/app/database/
├── __init__.py
├── base.py              ← DeclarativeBase (already exists)
├── connection.py        ← Engine + SessionLocal (already exists)
├── enums.py             ← All Python Enum classes
└── models/
    ├── __init__.py      ← Imports all models for Alembic autogenerate
    ├── instrument.py
    ├── candle.py
    ├── market_session.py
    ├── market_holiday.py
    ├── indicator_value.py
    ├── market_analysis.py
    ├── signal.py
    ├── risk_check.py
    ├── account.py
    ├── order.py
    ├── position.py
    ├── trade.py
    ├── setting.py
    ├── system_log.py
    └── decision_log.py
```

## 6.2 Alembic Migration (Phase 2C)

The first migration will:
1. Create all PostgreSQL `ENUM` types
2. Create all 15 tables in dependency order
3. Create all indexes and constraints

Migration filename: `001_initial_schema.py`

## 6.3 Testing (Phase 2D)

Tests will verify:
- All 15 tables are created successfully
- All unique constraints prevent duplicates
- All foreign key constraints work
- All enum values are accepted
- Nullable columns behave correctly
- `created_at` is set automatically
- `updated_at` is set automatically on mutable tables

---

# 7. Approval

```text
Reviewer        : ____________________
Date            : ____________________
Decision        : Approved / Rejected
Changes Needed  : ____________________
```

Once approved, change the document status at the top from `Draft` to `Approved` and proceed to Phase 2B.

---

END OF DOCUMENT